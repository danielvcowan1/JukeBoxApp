import { Component, ViewChild, ElementRef } from '@angular/core';
import { SpotifyAPIService } from 'src/app/services/spotifyAPI.service';
import { ApiService } from 'src/app/services/api.service';
import { interval } from 'rxjs/observable/interval';


@Component({
    selector: 'song-player',
    templateUrl: './song-player.component.html',
    styleUrls: ['./song-player.component.css']
})
export class SongPlayerComponent {
    playbackDevices: any = [];
    song: any;
    alreadyPlayed: any = [];
    @ViewChild('deviceSelect') deviceSelect:ElementRef;
    nextSongInterval: any;
    playbackSubscription: any;
    positionMs: number = 0;
    songPlaying: boolean = false;
    currentAlbum = '';
    currentArtist = '';
    currentSong = '';
    currentSpotifySongId = '';
    currentDuration: number = 0;

    constructor(private spotifyAPIService: SpotifyAPIService, private apiService: ApiService) {}

    getDevices(){
        if (this.deviceSelect.nativeElement.options.selectedIndex != 0)
            return; // don't fetch devices if user has selected one
        let spotifyId = localStorage.getItem('spotifyId');
        this.spotifyAPIService.getPlaybackDevices(spotifyId).subscribe(
            response => {
                console.log(response);
                this.playbackDevices = response['devices'];
            },
            error => {
                console.log(error);
                // handle error
            }
        );
    }

    onClickSkipToNextSong() {
        let selectedIndex = this.deviceSelect.nativeElement.options.selectedIndex;
        let deviceId = this.deviceSelect.nativeElement.options[selectedIndex].value;

        if (deviceId) {
            let playlistId = localStorage.getItem('activePlaylistId');
            if (playlistId) {
                this.skipToNextSong(playlistId, deviceId);
            } else {
                alert('Please open playlist before starting playback');
            }
        }
    }

    onClickStartPlayback() {
        let selectedIndex = this.deviceSelect.nativeElement.options.selectedIndex;
        let deviceId = this.deviceSelect.nativeElement.options[selectedIndex].value;
        console.log('Device ID: ' + deviceId + ' at index ' + selectedIndex);

        if (selectedIndex != 0 && deviceId){
            let playlistId = localStorage.getItem('activePlaylistId');
            if (playlistId) {
                this.startPlayback(playlistId, deviceId);
            } else {
                alert('Please open playlist before starting playback');
            }
        }
    }

    onClickPausePlayback() {
        let selectedIndex = this.deviceSelect.nativeElement.options.selectedIndex;
        let deviceId = this.deviceSelect.nativeElement.options[selectedIndex].value;

        if (deviceId) {
            this.pausePlayback(deviceId);
        }
    }

    private pausePlayback(deviceId) {
        this.apiService.getPlaybackInfo().subscribe(
            response => {
                // If nothing is playing query the playlist
               if (response != null && response['is_playing']) {
                    this.positionMs = response['progress_ms'];
                    this.playbackSubscription.unsubscribe();
                    this.apiService.pauseSong(deviceId).subscribe(
                        response => {
                            this.songPlaying = false;
                            console.log('Success');
                        }
                    );                         
                }
            },
            error => {
                console.log(error);
            }
        );
    }

    private terminatePlayback(){
        this.playbackSubscription.unsubscribe();
        this.songPlaying = false;
        this.currentAlbum = '';
        this.currentArtist = '';
        this.currentSong = '';
    }

    private hasAlreadyPlayed(song){
        for(var i = 0; i < this.alreadyPlayed.length; i++){
            if (this.alreadyPlayed[i] === song['spotify_song_id']){
                return true;
            }
        }
        return false;
    }

     private skipToNextSong(playlistId, deviceId) {
        this.apiService.getPlaybackInfo().subscribe(
            response => {
                // If nothing is playing query the playlist
                this.positionMs = this.currentDuration;
                if (response != null && response['is_playing']) {
                    this.playbackSubscription.unsubscribe();
                    this.apiService.pauseSong(deviceId).subscribe(
                        response => {
                            this.startPlayback(playlistId, deviceId);
                        }
                    );                         
                } else {
                    this.startPlayback(playlistId, deviceId);
                }
            },
            error => {
                console.log(error);
            }
        );
    }

    private startPlayback(playlistId, deviceId) {
        const NEXT_SONG = 1;
        const END_OF_PLAYLIST = 1;
        this.nextSongInterval = interval(1000);
        if (this.playbackSubscription) {
                this.playbackSubscription.unsubscribe(); // clear any existing intervals
        }
        this.playbackSubscription = this.nextSongInterval.subscribe(
            () => {
                //Check if a track is currently playing
                this.apiService.getPlaybackInfo().subscribe(
                    response => {
                        var playbackInfo = response;
                        // If nothing is playing query the playlist
                        if (response == null || !response['is_playing']) {
                            if (this.positionMs < (this.currentDuration - 2000)) {
                                console.log("RESUMING");
                                console.log(this.positionMs);
                                this.apiService.resumeSong(this.currentSpotifySongId, deviceId, this.positionMs).subscribe(
                                    response => {
                                        this.songPlaying = true;
                                        this.positionMs = playbackInfo['position_ms'];
                                    }, error => {
                                        console.log(error);
                                    } 
                                );
                            } else {
                                this.apiService.getPlaylist(playlistId).subscribe(
                                    response => {
                                        console.log("STARTING NEW SONG");
                                        var playlist: any = response;
                                        if(playlist.length == END_OF_PLAYLIST) {
                                            this.terminatePlayback();
                                        }
                                        this.currentAlbum = response[NEXT_SONG]['album'];
                                        this.currentArtist = response[NEXT_SONG]['artist'];
                                        this.currentSong = response[NEXT_SONG]['name'];
                                        this.currentSpotifySongId = response[NEXT_SONG]['spotify_song_id'];
                                        this.currentDuration = response[NEXT_SONG]['duration'];
                                        this.apiService.playSong(this.currentSpotifySongId, 
                                                                 deviceId, 
                                                                 playlistId).subscribe(
                                            response => {
                                                this.songPlaying = true;
                                            }
                                        );
                                    },
                                    error => {
                                    console.log(error);
                                }); 
                            }                          
                        }
                    },
                    error => {
                        console.log(error);
                    }
                );
            });

    }


    ngOnInit() {
        this.getDevices();
    }
}