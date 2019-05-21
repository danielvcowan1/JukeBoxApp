import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

/**
 * This service is for getting data through the API (backend)
 */
@Injectable({
  providedIn: 'root'
})
export class ApiService {

  apiURL: string = 'http://127.0.0.1:5000';

  constructor(private httpClient: HttpClient) { }

  private getAllowOriginHeaders(): any {
    return new HttpHeaders(
      {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token'
      }
    );
  }

  getData(): Observable<Object> {
    return this.httpClient.get(this.apiURL+'/json_test/');
  }

  obtainSpotifyAccessToken(accessCode: string, client_id: string,
                           client_secret: string, redirect_uri: string): Observable<Object> {
    let httpOptions = {
      headers: this.getAllowOriginHeaders()
    };
    let requestBody = {
      'code': accessCode,
      'client_secret': client_secret,
      'client_id': client_id,
      'redirect_uri': redirect_uri
    };
    return this.httpClient.post(this.apiURL+'/authenticate/', JSON.stringify(requestBody), httpOptions);
  }

  /**
   * This method creates a new playlist or pulls a playlist from the database
   * and 'activates' it, so that it is in memory in the server and joinable by Guests
   */
  activatePlaylist(name, description): Observable<Object> {
    let httpOptions = {
      headers: this.getAllowOriginHeaders()
    };
    let requestBody = {
      'name': name,
      'description': description,
      'spotify_id': localStorage.getItem('spotifyId')
    };
    //Post data to the backend 
    //console.log(this.apiURL + '/activate/', JSON.stringify(requestBody), httpOptions)
    return this.httpClient.post(this.apiURL + '/activate/', JSON.stringify(requestBody), httpOptions);
  }

  getPlaylist(pId?, pCode?) {
    var spotify_id = '?spotify_id=' + localStorage.getItem('spotifyId');
    var playlist_id = pId == undefined ? '' : '&playlist_id=' + pId; // Pass the ID unless it's a new playlist
    var playlist_code = pCode == undefined ? '' : '&playlist_code=' + pCode;
    //console.log(this.apiURL + '/load/' + spotify_id + playlist_id + playlist_code);
    return this.httpClient.get(this.apiURL + '/load/' + spotify_id + playlist_id + playlist_code);

  }

  deletePlaylist(pId) {
    var spotify_id = '?spotify_id=' + localStorage.getItem('spotifyId');
    var playlist_id = '&playlist_id=' + pId;
    console.log(this.apiURL + '/delete/' + spotify_id + playlist_id);
    return this.httpClient.get(this.apiURL + '/delete/' + spotify_id + playlist_id);
  }

  addSongToPlaylist(pId, song: any): Observable<Object> {
      let httpOptions = {
        headers: this.getAllowOriginHeaders()
      };
      let requestBody = {
        'playlist_id': pId,
        'name': song['name'],
        'spotify_song_id': song['id'],
        'artist': song['artist'],
        'album': song['album'],
        'duration': song['duration']
      };
      console.log(this.apiURL + '/add/', JSON.stringify(requestBody), httpOptions);
      return this.httpClient.post(this.apiURL + '/add/', JSON.stringify(requestBody), httpOptions);
  }

  guestAddSongToPlaylist(pId, song: any): Observable<Object> {
      let httpOptions = {
        headers: this.getAllowOriginHeaders()
      };
      let requestBody = {
        'playlist_id': pId,
        'name': song['name'],
        'spotify_song_id': song['id'],
        'artist': song['artist'],
        'album': song['album'],
        'duration': song['duration']
      };
      console.log(this.apiURL + '/add/', JSON.stringify(requestBody), httpOptions);
      return this.httpClient.post(this.apiURL + '/add/', JSON.stringify(requestBody), httpOptions);
  }

  deleteSongFromPlaylist(pId, songSpotifyId) {
    var spotify_id = '?spotify_id=' + localStorage.getItem('spotifyId');
    var playlist_id ='&playlist_id=' + pId;
    var song_id = '&song_id=' + songSpotifyId;
    console.log(this.apiURL + '/delete_song/' + spotify_id + playlist_id + song_id);
    return this.httpClient.get(this.apiURL + '/delete_song/' + spotify_id + playlist_id + song_id);
  }

  upvoteSong(dbSongId): Observable<Object> {
    return this.voteSong(dbSongId, 1);
  }

  downvoteSong(dbSongId): Observable<Object> {
    return this.voteSong(dbSongId, -1);
  }

  private voteSong(dbSongId, voteVal: number) {
    let httpOptions = {
      headers: this.getAllowOriginHeaders()
    };
    let requestBody = {
      'playlist_id': localStorage.getItem('activePlaylistId'),
      'spotify_id': localStorage.getItem('spotifyId'),
      'vote_value': voteVal,
      'song_id': dbSongId
    };
    return this.httpClient.post(this.apiURL + '/vote_song/', JSON.stringify(requestBody), httpOptions);
  }

  getNextTrack(pId){
    var spotify_id = '?spotify_id=' + localStorage.getItem('spotifyId');
    var playlist_id = pId == -1 ? '' : '&playlist_id=' + pId;
    return this.httpClient.get((this.apiURL + '/get_next_song/' + spotify_id + playlist_id))
  }

  getPlaybackInfo(playlistId?){
    if (playlistId == undefined) {
        var spotify_id = '?spotify_id=' + localStorage.getItem('spotifyId');
        return this.httpClient.get((this.apiURL + '/playback/' + spotify_id))
      } else {
        var playlist_id = '?playlist_id=' + playlistId;
        return this.httpClient.get((this.apiURL + '/playback/' + playlist_id))
      }
  }

  pauseSong(deviceId) {
    let httpOptions = {
      headers: this.getAllowOriginHeaders()
    };
    let requestBody = {
      'spotify_id': localStorage.getItem('spotifyId'),
      'device_id': deviceId
    };
    console.log('PAUSING SONG');
    return this.httpClient.post(this.apiURL + '/playback/pause/',
                                JSON.stringify(requestBody),
                                httpOptions);
  }

  playSong(songUri, deviceId, playlistId) {
    let httpOptions = {
      headers: this.getAllowOriginHeaders()
    };
    let requestBody = {
      'spotify_id': localStorage.getItem('spotifyId'),
      'uri': songUri,
      'device_id': deviceId,
      'playlist_id': playlistId
    };
    console.log(songUri + ' ' + deviceId);
    console.log('PLAYING SONG ');
    return this.httpClient.post(this.apiURL + '/playback/play/', 
                                JSON.stringify(requestBody), 
                                httpOptions);
  }

  resumeSong(songUri, deviceId, positionMs) {
    let httpOptions = {
      headers: this.getAllowOriginHeaders()
    };
    let requestBody = {
      'spotify_id': localStorage.getItem('spotifyId'),
      'uri': songUri,
      'device_id': deviceId,
      'position': positionMs
    };
    console.log(songUri + ' ' + deviceId);
    return this.httpClient.post(this.apiURL + '/playback/resume/', 
                                JSON.stringify(requestBody), 
                                httpOptions);
  }
}
