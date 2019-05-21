import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { SpotifyAPIService } from 'src/app/services/spotifyAPI.service';
import { ApiService } from 'src/app/services/api.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'playlist-display',
  templateUrl: './playlist-display.component.html',
  styleUrls: ['./playlist-display.component.css']
})
export class PlaylistDisplayComponent implements OnInit {

  playlists: any = [];
  playlistsHidden: boolean = false;
	@Output() selectPlaylistEvent = new EventEmitter();
	
  constructor(private spotifyAPIService: SpotifyAPIService,
              private apiService: ApiService,
              private modalService: NgbModal) { 
  }

  ngOnInit() {
    this.getPlaylists();
  }

  private getPlaylists() {
    var spotifyId = localStorage.getItem('spotifyId');
    this.spotifyAPIService.getUserPlaylists(spotifyId).subscribe(
      response => {
        this.playlists = response;
      },
      error => {
      console.log(error);
      }
    );
  }

  private activateNewPlaylist(name: string, description: string) {
    console.log("Get data from form inputs and post to API");
    //Get input values
    // Pass to api service to create playlist on flask api
    this.apiService.activatePlaylist(name, description).subscribe(
      response => {
        console.log(response);
        this.playlists = response;
      },
      error => {
        console.log(error);
      }
    );
  }

  private deletePlaylist(playlistId) {
    this.apiService.deletePlaylist(playlistId).subscribe(
      response => {
      console.log(response);
      this.playlists = response;
      },
      error => {
        console.log(error);
      }
    );
  }

  private emitPlaylistSelection(selectPlaylistEvent: Event, playlistId) {
    console.log("Select playlist id: " + playlistId);
    localStorage.setItem('activePlaylistId', playlistId);
    this.selectPlaylistEvent.emit(playlistId);
    this.playlistsHidden = true; // auto-collapse display
  }

  private activateExistingPlaylist(playlist_id) {
    this.apiService.getPlaylist(playlist_id);
  }

  /**
   * Opens the modal dialog prompting user for new playlist details
   */
  createNewPlaylist(content) {
    this.modalService.open(content, {ariaLabelledBy: 'modal-basic-title'}).result.then(
      (result) => {
        if (result) {
          this.activateNewPlaylist(result['name'], result['description']);
        }
      },
      (reason) => { }
    );
  }
}
