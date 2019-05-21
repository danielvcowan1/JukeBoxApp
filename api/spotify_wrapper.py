import spotipy
from spotipy import Spotify
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import SpotifyException
CLIENT_ID = 'CLIENT_ID_HERE'
CLIENT_SECRET = 'CLIENT_SECRET_HERE'
REDIRECT_URI = 'http://127.0.0.1:4200/host'
SEARCH_LIMIT = 10
#client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
#spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


class Song:

    def __init__(self, song_data):
        self.data = song_data
        self.SMALL_IMAGE = 2
        self.MEDIUM_IMAGE = 1
        self.LARGE_IMAGE = 0

    def get_name(self):
        return self.data['name']

    def get_artist(self):
        return self.data['artists'][0]['name']

    def get_id(self):
        return self.data['id']

    def get_album(self):
        return self.data['album']['name']

    def get_album_image(self, size=1):
        return self.data['album']['images'][size]['url']

    def get_duration(self):
        return self.data['duration_ms']

    def get_song_data(self):
        return {'name': self.get_name(),
                'artist': self.get_artist(),
                'id': self.get_id(),
                'album': self.get_album(),
                'image_url': self.get_album_image(),
                'duration': self.get_duration()}


class SearchResult:
    def __init__(self, results):
        self.data = results
        self.tracks = self.data['tracks']['items']
        self.parsed_data = self._parse_data()

    def _parse_data(self):
        search_result = []
        for track in self.tracks:
            song = Song(track)
            song_data = song.get_song_data()
            search_result.append(song_data)

        return search_result

    def get_data(self):
        return self.parsed_data


class SpotifyWrapper:
    SEARCH_LIMIT = 50

    def __init__(self, token):
        self.token = token
        self.spotify = Spotify(auth=self.token)

    def search_songs(self, q, limit=SEARCH_LIMIT):

        results = self.spotify.search(
            q, limit=limit, type='track', market=None)
        sr = SearchResult(results)
        return sr.get_data()

    def valid_token(self):
        try:
            self.spotify.search(
                'test call', limit=1, type='track')
            print('Token OK')
            return True
        except SpotifyException as e:
            print('INVALID TOKEN')
            return False


    def get_playback_devices(self):
        devices = self.spotify.devices()
        print(devices)
        return devices

    @staticmethod
    def get_token(code):
        pass



# Authorize user
def authorize(username):
    # Authorization scopes:
    # https://developer.spotify.com/documentation/general/guides/scopes/
    token = util.prompt_for_user_token(
        username=username,
        scope='user-modify-playback-state user-read-currently-playing playlist-modify-private',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI)
    if (token):
        print("Valid token")
        spotify = spotipy.Spotify(token)

# Get playlists owned by user


def get_user_playlists(username):
    return spotify.user_playlists(user=username, limit=10, offset=0)

# Get specific playlist owned by user


def get_user_playlist(username, playlist_id):
    results = spotify.user_playlist(
        user=username,
        playlist_id=playlist_id,
        fields='tracks, name')
    print(results['name'])
    print(results['tracks']['total'])
    items = results['tracks']['items']
    for track in items:
        print(track['track']['name'])
    return results


# Search for tracks by name
def search_track(q, limit=10, offset=0, market=None):
    query = 'track:' + q
    results = spotify.search(query, limit, offset, 'track', market)
    items = results['tracks']['items']
    if len(items) > 0:
        # for track in items:
        track = items[0]
        print(track['name'] + " " + track['id'])

# Search for artists by name


def search_artist(q, limit=10, offset=0, market=None):
    query = 'artist:' + q
    results = spotify.search(query, limit, offset, 'artist', market)
    items = results['artists']['items']
    if len(items) > 0:
        # for artist in items:
        artist = items[0]
        print(artist['name'] + " " + artist['id'])

# Search for album by name


def search_album(q, limit=10, offset=0, market=None):
    query = 'album:' + q
    results = spotify.search(query, limit, offset, 'album', market)
    items = results['albums']['items']
    if len(items) > 0:
        # for album in items:
        album = items[0]
        print(album['name'] + " " + album['id'])

# Query for tracks, artists, or album
# q - query string
# limit - number of results returned
# type - category we're querying (e.g. track name, artist, album)


def search(q, limit=10, type='track'):
    if type == 'track':
        search_track(q, limit=10, offset=0, market=None)
    elif type == 'artist':
        search_artist(q, limit=10, offset=0, market=None)
    else:
        search_album(q, limit=10, offset=0, market=None)


# TODO
# def play_song(songId):

# TODO
# def get_next_song(playlist_id, current_position):

# Add a list of tracks to user's playlist
# username - the authorized/host user
# playlist_id - the playlist id of the playlist we want to add tracks to (owned by host)
# tracks - list of track URIs, URLs, or IDs (we will probably be using track ids since that's our Song implementation)
# position - where in the playlist to add the tracks --> 0 indexed; if
# left as None, the tracks will be appended to end (probably can
# ignore/remove for our purposes)
def save_playlist(username, playlist_id, tracks, position=None):
    # TODO: only add tracks if they don't already exist
    spotify.user_playlist_add_tracks(username, playlist_id, tracks, position)


# authorize('segao')
# print(get_user_playlists('segao'))
# Currently having authorization problems for write and playback methods
# Maybe I'm using the wrong scope?
# save_playlist('segao', '4BOUeKhccYjavP2FoJUP43', ['5OCJzvD7sykQEKHH7qAC3C'])
#get_user_playlist('segao', '4BOUeKhccYjavP2FoJUP43')

#search(q='Radiohead', type='artist')
#search(q='God is a woman', type='track')
#search(q='stairway to heaven', type='album')
