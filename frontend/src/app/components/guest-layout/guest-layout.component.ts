import { Component, ViewChild, ElementRef, Output, EventEmitter } from '@angular/core';
import { ApiService } from 'src/app/services/api.service';
import { interval } from 'rxjs/observable/interval';

/**
 * Guest user interface
 */
@Component({
  selector: 'guest-layout',
  templateUrl: './guest-layout.component.html',
  styleUrls: ['./guest-layout.component.css']
})

export class GuestLayoutComponent {
  @ViewChild('connectInput') input:ElementRef;
  public guestSongData: any = [];

  private connected: Boolean = false;
  private invalidCode: Boolean = false;
  private connectedPlaylistId = '';
  private currentlyPlayingSongId = '';
  private currentlyPlayingSong = '';
  private currentlyPlayingArtist = '';

  constructor(private apiService: ApiService) { }

  ngOnInit() {
    const intv = interval(1000);
    intv.subscribe(
      () => {
        this.pollPlayingSong();
      });
  }

  private connectToPlaylist(accessPlaylistEvent: Event) {
    let accessCode = this.input.nativeElement.value.toUpperCase();
    this.apiService.getPlaylist(undefined, accessCode).subscribe(
          (response: Array<Object>) => {
            if (response[0] != "INVALID") {
              this.connected = true;
              this.guestSongData = response;
              this.connectedPlaylistId = response[0]['IDPlaylist'];
              this.invalidCode = false;
            } else {
              this.connected = false;
              this.guestSongData = [];
              this.invalidCode = true;
            }
            console.log(response);
          },
          error => {
            console.log(error);
          }
        );
    console.log("Attempting to access playlist with code: " + accessCode);  
  }

  private pollPlayingSong() {
    if (this.connectedPlaylistId != '') {
      this.apiService.getPlaybackInfo(this.connectedPlaylistId).subscribe(
        response => {
            if (response != null && response['is_playing']) {
              var playback: any = response;
              if (playback['item']['id'] != this.currentlyPlayingSongId) {
                this.currentlyPlayingSongId = playback['item']['id'];
              }
              this.getCurrentlyPlayingSongInfo();
            } else {
              this.currentlyPlayingSong = '';
            }
        },error => {
              console.log(error);
          }
      );
    }
  }

  private getCurrentlyPlayingSongInfo() {
    for (var index in this.guestSongData) {
      if (this.guestSongData[index]['spotify_song_id'] == this.currentlyPlayingSongId) {
        this.currentlyPlayingSong = this.guestSongData[index]['name'];
        this.currentlyPlayingArtist = this.guestSongData[index]['artist'];
        break;
      }
    }
  }

}