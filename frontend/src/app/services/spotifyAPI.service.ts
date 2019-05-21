import { Injectable, Inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { HttpHeaders } from '@angular/common/http';
import { ApiService } from './api.service';

@Injectable({
    providedIn: 'root'
})

export class SpotifyAPIService {

    private apiURL: string = 'http://127.0.0.1:5000';
    private client_id: string = 'CLIENT_ID_HERE';
    private client_secret: string = 'CLIENT_SECRET_HERE';
    private redirect_uri: string = 'http://127.0.0.1:4200/host';
    private scopes: string = 'user-read-private playlist-read-private playlist-modify-private playlist-modify-public user-read-playback-state user-modify-playback-state';
    private access_token: string;
    private user_id: string;

    constructor(private httpClient: HttpClient,
                private apiService: ApiService) { }

    private loginURL: string =  'https://accounts.spotify.com/authorize' +
                                '?response_type=code' +
                                '&client_id=' + this.client_id +
                                (this.scopes ? '&scope=' + this.scopes : '') +
                                '&redirect_uri=' + this.redirect_uri +
                                '&show_dialog=true';

    getLoginURL(): string {
        return this.loginURL;
    }

    getUserId(): string {
        return this.user_id;
    }

    /**
     * Makes request to backend to obtain the access token and user id.
     * @param accessCode
     */
    obtainAccessToken(accessCode: string): Observable<Object> {
        return this.apiService.obtainSpotifyAccessToken(accessCode,
                                                        this.client_id,
                                                        this.client_secret,
                                                        this.redirect_uri);
    }

    checkAccessToken(spotifyId: string){
        let id = '?spotify_id=' + spotifyId;
        return this.httpClient.get((this.apiURL + '/authenticate/token/' + id));
    }


    /** returns the current user's spotify user data
    * @param spotifyId
    */
    getUserData(spotifyId: string){
        let id = '?spotify_id=' + spotifyId;
        return this.httpClient.get((this.apiURL + '/myself/' + id));
    }
    /** returns the current user's playlists
    * @param spotifyId
    */
    getUserPlaylists(spotifyId: string){
        let id = '?spotify_id=' + spotifyId;
        return this.httpClient.get((this.apiURL + '/playlists/' + id));
    }

    /** returns playback devices for current user
     * @param spotify id
     *
     */
    getPlaybackDevices(spotifyId: string){
        let id = '?spotify_id=' + spotifyId;
        return this.httpClient.get((this.apiURL + '/playback/devices/' + id))
    }

    /**
     * Need to call this when getting successful response from obtainAccessToken().
     * @param id User ID
     * @param token Access Token
     */
    setUserIdAccessToken(id: string, token: string): void {
        this.user_id = id;
        this.access_token = token;
    }

    /**
     * Returns Observable from spotify search GET request.
     * @param spotifyId Spotify User ID
     * @param searchString Search parameter
     * @param searchType Artist, album, etc
     */
    querySpotifyApi(spotifyId:string, searchString:string, 
                    searchType: string): Observable<Object> {

      let qryString =  '?search_string=' + searchString + 
                       '&search_type=' + searchType +
                       '&spotify_id=' + spotifyId;

      return this.httpClient.get((this.apiURL + '/search/' + qryString));
    }
    querySpotifyApiAsGuest(playlistId:string, searchString:string, 
                    searchType: string): Observable<Object> {
        console.log('searching as guest');
        let qryString = '?search_string=' + searchString +
                        '&guest_search=true' +
                        '&playlist_id=' + playlistId;

        return this.httpClient.get((this.apiURL + '/search/' + qryString));

    }
}


