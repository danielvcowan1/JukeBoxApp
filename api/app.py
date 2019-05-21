from flask import (
    request,
    session,
    url_for,
    redirect,
    render_template,
    abort,
    Flask,
    jsonify
)
from flask_cors import CORS, cross_origin
from spotipy import oauth2, Spotify
from config import Config
from database import Database
from spotify_wrapper import SpotifyWrapper
from playlist import Playlist
from song import Song
import requests
import random
import string


app = Flask(__name__)
CORS(app)
app.secret_key = 'secret key used to set session variables (cookies)'

CODE_LENGTH = 4
code_to_playlist = dict() # map playlist codes to active playlist objects (or maybe IDs?)
userID_to_code = dict()  # This dictionary will map spotify IDs to playlist codes
song_objects = dict() # manages all song objects in memory (song = song_objects[SONG_ID])


@app.route('/playlists/', methods=['GET'])
def get_user_playlists():

    """Returns all user playlists stored in database"""

    user_id = request.args.get('spotify_id')
    if user_id:
        db = Database(Config.DATABASE_PATH)
        playlists = db.get_user_playlists(user_id)
        return create_response(playlists)
        
    return jsonify({'Error': 'Invalid or missing spotify id'})

""" TODO:
    This method will take a playlist from the db or a new playlist,
    assign it a code and keep it active in dict so that it can be joined
    note that by 'code' I'm referring to the join code, not the playlist's
    ID in the database
    """
@app.route('/activate/', methods=['GET', 'POST'])
def activate_playlist():
    playlist_data = request.get_json(force=True)

    if (not playlist_data['spotify_id'] or
        not playlist_data['name'] or
        not playlist_data['description']):
        return abort(400, 'invalid request parameters')

    db = Database(Config.DATABASE_PATH)
    # generate access code
    playlist_data['access_code'] = gen_playlist_code()
    # save new playlist
    db.save_playlist(playlist_data)
    # get all user playlists to return
    playlists = db.get_user_playlists(playlist_data['spotify_id'])

    return create_response(playlists)

@app.route('/load/', methods=['GET'])
def load_playlist():
    spotify_id = request.args.get('spotify_id')
    playlist_id = request.args.get('playlist_id')
    playlist_code = request.args.get('playlist_code')

    if spotify_id:
        db = Database(Config.DATABASE_PATH)
        if playlist_id:
            name_access_code = db.get_playlist_name_and_access_code(playlist_id)
            playlist = db.get_user_playlist(playlist_id)
            # need to create playlist object if not already created
            if playlist_code not in code_to_playlist:
                create_playlist_object(playlist_id, playlist, name_access_code[0]['AccessCode'])
            get_playlist_votes(playlist)
            return create_response(name_access_code + playlist)
        elif playlist_code: # guest entering access code to get playlist
            valid_code = db.check_access_code_is_valid(playlist_code)
            if not valid_code:
                return create_response(["INVALID"])
            playlist_and_code = db.get_playlist_with_access_code(playlist_code)
            playlist_info = playlist_and_code[0] # name, access code, id
            playlist = playlist_and_code[1:len(playlist_and_code)]  # songs in the playlist
            # need to create playlist object if not already created
            if playlist_code not in code_to_playlist:
                create_playlist_object(playlist_info['IDPlaylist'], playlist, playlist_info['AccessCode'])
            get_playlist_votes(playlist)
            return create_response([playlist_info] + playlist)
    return abort(400, 'invalid request parameters')

@app.route('/add/', methods=['GET', 'POST'])
def add_song_to_playlist():
    song_data = request.get_json(force=True)
    print(song_data)
    if (not song_data['spotify_song_id'] or
        not song_data['name'] or
        not song_data['artist'] or
        not song_data['album'] or
        not song_data['playlist_id'] or
        not song_data['duration']):
        print('Error: add song to playlist failed')
        return abort(400, 'invalid request parameters')
    db = Database(Config.DATABASE_PATH)
    song_id = db.add_song_to_playlist(song_data['playlist_id'], song_data)
    print(song_id)
    # create song object
    song_objects[song_id] = Song(song_data['spotify_song_id'], 
                                 song_data['name'],  
                                 song_data['artist'], 
                                 song_data['album'], 
                                 None, 
                                 0,
                                 song_data['duration'])
    #find the associated playlist object
    name_access_code = db.get_playlist_name_and_access_code(song_data['playlist_id']) #gets name and access code from database

    try:
        #returns playlist object given access code
        playlist = code_to_playlist.get(name_access_code[0]['AccessCode'])
        #add this song object to its playlist object
        playlist.addSong(song_objects[song_id])
        refreshed_playlist = db.get_user_playlist(song_data['playlist_id'])
        # update refreshed playlist with current vote counts
        get_playlist_votes(refreshed_playlist)
        return create_response(refreshed_playlist)
    except NameError as e:
        # pull playlist from db if not found in memory
        refreshed_playlist = db.get_playlist(song_data['playlist_id'])
        return create_response(refreshed_playlist)

@app.route('/playback/', methods=['GET'])
def get_current_playback():
    spotify_id = request.args.get('spotify_id')
    playlist_id = request.args.get('playlist_id')

    if playlist_id:
        db = Database(Config.DATABASE_PATH)
        token = db.get_host_token(playlist_id)
        spotify = Spotify(auth=token)
        playback = spotify.current_playback()
        return create_response(playback)
    elif spotify_id:
        db = Database(Config.DATABASE_PATH)
        token = db.get_user_token(spotify_id)
        spotify = Spotify(auth=token)
        playback = spotify.current_playback()
        return create_response(playback)

    return jsonify({'Error': 'Invalid or missing spotify id'})


@app.route('/playback/play/', methods=['POST'])
def play_song():
    play_req = request.get_json(force=True)
    spotify_id = play_req['spotify_id']
    dev_id = play_req['device_id']
    uri = "spotify:track:" + play_req['uri']
    playlist_id = play_req['playlist_id']

    if spotify_id:
        db = Database(Config.DATABASE_PATH)
        token = db.get_user_token(spotify_id)
        spotify = Spotify(auth=token)
        print('PLAYING SONG')
        play_data = spotify.start_playback(device_id=dev_id, uris=[uri])
        db.delete_song_from_playlist(playlist_id, play_req['uri'])
        
        return create_response(play_data)

    return jsonify({'Error': 'Invalid or missing spotify id'})

@app.route('/playback/resume/', methods=['POST'])
def resume_song():
    resume_req = request.get_json(force=True)
    spotify_id = resume_req['spotify_id']
    dev_id = resume_req['device_id']
    uri = "spotify:track:" + resume_req['uri']
    position_ms = resume_req['position']

    if spotify_id:
        db = Database(Config.DATABASE_PATH)
        token = db.get_user_token(spotify_id)
        spotify = Spotify(auth=token)
        print('RESUMING SONG')
        play_data = spotify.start_playback(device_id=dev_id, uris=[uri])
        spotify.seek_track(position_ms=position_ms, device_id=dev_id)
        return create_response(play_data)

    return jsonify({'Error': 'Invalid or missing spotify id'})

@app.route('/playback/pause/', methods=['POST'])
def pause_song():
    pause_req = request.get_json(force=True)
    spotify_id = pause_req['spotify_id']
    dev_id = pause_req['device_id']

    if spotify_id:
        db = Database(Config.DATABASE_PATH)
        token = db.get_user_token(spotify_id)
        spotify = Spotify(auth=token)
        print('PAUSING SONG')
        pause_data = spotify.pause_playback(device_id=dev_id)
        return create_response(pause_data)

    return jsonify({'Error': 'Invalid or missing spotify id'})

def get_current_user():
    """Retrieves information for the current user"""
    user_id = request.args.get('spotify_id')

    if user_id:
        db = Database(Config.DATABASE_PATH)
        token = db.get_user_token(user_id)
        spotify = Spotify(auth=token)
        user = spotify.current_user()
        return create_response(user)

    return jsonify({'Error': 'Invalid or missing spotify id'})

@app.route('/delete_song/', methods=['GET'])
def delete_song_from_playlist():
    spotify_id = request.args.get('spotify_id')
    playlist_id = request.args.get('playlist_id')
    song_id = request.args.get('song_id')
    if (not spotify_id or not playlist_id or not song_id):
        return abort(400, 'invalid request parameters')
    db = Database(Config.DATABASE_PATH)
    db.delete_song_from_playlist(playlist_id, song_id)
    refreshed_playlist = db.get_user_playlist(playlist_id)
    # update refreshed playlist with current vote counts
    get_playlist_votes(refreshed_playlist)
    return create_response(refreshed_playlist)
    
@app.route('/delete/', methods=['GET'])
def delete_playlist():
    spotify_id = request.args.get('spotify_id')
    playlist_id = request.args.get('playlist_id')
    if spotify_id and playlist_id:
        db = Database(Config.DATABASE_PATH)
        db.delete_playlist(playlist_id)
        refreshed_playlists = db.get_user_playlists(spotify_id)
        return create_response(refreshed_playlists)
    if not spotify_id:
        return abort(400, 'Did not specify spotify id')
    if not playlist_Id:
        return abort(400, 'Did not specify playlist id')


@app.route('/vote_song/', methods=['POST'])
def vote_song():
    vote_data = request.get_json(force=True)
    user_id = vote_data['spotify_id']
    playlist_id = vote_data['playlist_id']
    vote_value = vote_data['vote_value']
    song_id = vote_data['song_id']

    if not user_id:
        user_id = "GUEST"
    if not playlist_id:
        return abort(400, 'Did not specify playlist id')
    if not vote_value:
        return abort(400, 'Did not specify vote value')
    if not song_id:
        return abort(400, 'Did not specify db song id')

    db = Database(Config.DATABASE_PATH)
    db.vote_song(user_id, song_id, playlist_id, vote_value)
    # update song object
    try:
        # update in-memory objects
        song_objects[song_id].voteCount += vote_value
        refreshed_playlist = db.get_user_playlist(playlist_id)
        # update refreshed playlist with current vote counts
        get_playlist_votes(refreshed_playlist)
        return create_response(refreshed_playlist)
    except (KeyError, NameError):
        # if in memory object not found, get pl from db
        refreshed_playlist = db.get_playlist(playlist_id)
        return create_response(refreshed_playlist)

### TODO: Implement 'get next song' endpoint
### this endpoint should return the next song (just spotify song id) AND an updated playlist
@app.route('/get_next_song/', methods=['GET'])
def get_next_song():
    user_id = request.args.get('spotify_id')
    playlist_id = request.args.get('playlist_id')
    if user_id and playlist_id:
        db = Database(Config.DATABASE_PATH)
        name_access_code = db.get_playlist_name_and_access_code(playlist_id) #gets name and access code from database
        playlist = code_to_playlist.get(name_access_code[0]['AccessCode']) #returns playlist object given access code
        song_to_play = playlist.getNextSong() #returns song object
        #song_to_play_title = song_to_play[1].get_title()
        #print(song_to_play_title)
        song_to_play_id = song_to_play[1].get_id() #returns the id of that song object
        #print(song_to_play_id)
        return create_response(song_to_play_id)
    if not user_id:
        return abort(400, 'Did not specify spotify id')
    if not playlist_Id:
        return abort(400, 'Did not specify playlist id')
    # here we can call code_to_playlist[playlist_access_code].getNextSong() to get
    # the 'Song' object for the next song, and return spotify_id of this song in the response.

@app.route('/myself/', methods=['GET'])
def get_current_user():
    """Retrieves information for the current user"""
    user_id = request.args.get('spotify_id')

    if user_id:
        db = Database(Config.DATABASE_PATH)
        token = db.get_user_token(user_id)
        spotify = Spotify(auth=token)
        user = spotify.current_user()
        return create_response(user)

    return jsonify({'Error': 'Invalid or missing spotify id'})


@app.route('/search/', methods=['GET'])
def search_spotify():
    """Searches the spotify API"""
    # TODO: figure out limit for search results
    guest_search = request.args.get('guest_search')
    query =  request.args.get('search_string')

    # Check that url is well formed
    if not query:
        return abort(400, 'missing parameters')

    if guest_search:
        playlist_id = request.args.get('playlist_id')
        if playlist_id:
            db = Database(Config.DATABASE_PATH)
            token = db.get_host_token(playlist_id)

            if not token:
                return abort(400, 'something went wrong')

            spotify = SpotifyWrapper(token)
            print('Searching as guest for: ', query)
            search_results = spotify.search_songs(query)
            return create_response(search_results)
    else:
        db = Database(Config.DATABASE_PATH)
        # Get query strings
        user_id = request.args.get('spotify_id')

        #Get user token stored in db
        token = db.get_user_token(user_id)

        if token:
            spotify = SpotifyWrapper(token)
            print('Searching as host for: ', query)
            search_results = spotify.search_songs(query)
            # create & return response 
            return create_response(search_results)

        return abort(400, 'Authentication Required')



@app.route('/playback/devices/', methods=['GET'])
def get_playback_devices():
    user_id = request.args.get('spotify_id')
    if not user_id:
        return abort(400, 'Did not specify spotify id')

    db = Database(Config.DATABASE_PATH)
    token = db.get_user_token(user_id)
    if token:
        spotify = Spotify(auth=token)
        devices = spotify.devices()
        return create_response(devices) 

    return abort(401, 'Authentication required')


@app.route('/authenticate/', methods=['POST'])
def obtain_access_token():

    """Post authorization code to 'https://accounts.spotify.com/api/token'
       and obtain access token
    """
    # get dict from spotifyAPIService.obtainAccessToken(code) function
    access_data = request.get_json(force=True)
    auth_data = {
        'grant_type': 'authorization_code',
        'code': access_data['code'],
        'redirect_uri': 'http://127.0.0.1:4200/host',
        'client_secret': access_data['client_secret'],
        'client_id': access_data['client_id']

    }
    # do another post to get the token
    resp = requests.post(Config.SPOTIFY_TOKEN_URL, data=auth_data)

    # If successful
    if resp.status_code == 200:
        token = resp.json()['access_token']
        spotify = Spotify(auth=token)
        user = spotify.current_user()
        db = Database(Config.DATABASE_PATH)
        existing_user = db.get_user(user['id'])

        # Check if user exists in local db
        if not existing_user:
            # if not, then add them to db w/ access token 
            db.add_user(user['display_name'], user['id'], token)
            print('user added to db')
        else:
            # If they exist, update db with fresh token
            db.update_user_token(user['id'], token)
            print('updated user token')

        print(user['display_name'], 'is now logged into spotify')

        # return user info to front end

        return create_response({'token': token,
                                'id': user['id'],
                                'display_name': user['display_name']})
    else:
        abort(resp.status_code)

@app.route('/authenticate/token/', methods=['GET'])
def check_token():
    user_id = request.args.get('spotify_id')
    if not user_id:
        return abort(400, 'did not specify spotify id')

    db = Database(Config.DATABASE_PATH)
    token = db.get_user_token(user_id)
    if token:
        spotify = SpotifyWrapper(token)
        token_status = {
            'token status': spotify.valid_token(),
            'token': token,
            'id': user_id
        }
        return create_response(token_status)
    else:
        token_status = {'token status': False}
        return create_response(token_status)



@app.route("/json_test/", methods=['GET'])
def json_test():

    nested_dict = {
        'nested data': "nested test data"
    }

    json_dict = {
        'data': 'Test Data',
        'nested_data': nested_dict

    }

    # jsonify method converts python data structures into
    # JSON objects
    response = jsonify(json_dict)

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
def create_response(data_dict):
    response = jsonify(data_dict)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def gen_playlist_code():
    playlist_code = ''
    while playlist_code == '' or playlist_code in code_to_playlist:
        playlist_code = ''.join(random.choice(string.ascii_uppercase)
                                for _ in range(CODE_LENGTH))
    return playlist_code

# Creates a playlist object, all song objects for that playlist, and registers song and 
# playlist objects in code_to_playlist and song_objects
def create_playlist_object(playlist_db_id, songs, access_code):
    playlist_obj = Playlist()
    for song in songs:
        # get vote count for song
        db = Database(Config.DATABASE_PATH)
        vote_count = db.get_song_votes(song['id'], playlist_db_id)
        # create song object
        s = Song(song['spotify_song_id'], song['name'], song['artist'], song['album'], None, vote_count, song['duration'])
        s_id = song['id']
        song_objects[s_id]= s
        playlist_obj.addSong(s)
    code_to_playlist[access_code] = playlist_obj

# Acts on playlist (array of songs) and appends the vote count for each song
# Will sort songs by vote count
def get_playlist_votes(songs):
    song_votes = []
    for song in songs:
        song['votes'] = song_objects[song['id']].voteCount
    songs.sort(key = lambda song: song['votes'], reverse=True)

if __name__ == '__main__':
    db = Database(Config.DATABASE_PATH)
    app.run(debug=True)


