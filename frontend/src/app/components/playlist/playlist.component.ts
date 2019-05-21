import { Component, Input, SimpleChanges } from '@angular/core';
import { ApiService } from 'src/app/services/api.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { interval } from 'rxjs/observable/interval';

@Component({
    selector: 'playlist',
    templateUrl: './playlist.component.html',
    styleUrls: ['./playlist.component.css']
})
export class PlaylistComponent {
    @Input() accessedSongData: any;
    @Input() canDelete: boolean;
    @Input() condensedView: boolean;

    playlistName = '';
    playlistCode = '';

    songData: any = [];
    votes: any = {};

    playStates: any = new Map<string, boolean>();
    lastPlayedSongId: any;
    upvotes: any = new Map<string, boolean>();
    downvotes: any = new Map<string, boolean>();

    ngOnChanges(changes: SimpleChanges) {
    	if (changes['accessedSongData']) {
	        var change = changes['accessedSongData'].currentValue;
	        if (change[0]) {
	            var playlistInfo = change.shift();
	            this.playlistName = playlistInfo['Name'];
	            this.playlistCode = playlistInfo['AccessCode'];
	            localStorage.setItem('activePlaylistId', playlistInfo['IDPlaylist']);
	        } else {
	            this.playlistName = '';
	            this.playlistCode = '';
	        }
	        this.setSongData(change);
    	}
    }

    ngOnInit(){
        localStorage.removeItem('activePlaylistId');
        const intv = interval(500);
        intv.subscribe(
        	() => {
        		this.pollPlaylist();
        	});
    }


    constructor(private apiService: ApiService,
                private modalService: NgbModal) { }

    /**
     * This function is called when a song is added from the search component.
     */
    addSong(song: any) {
        var playlistId = localStorage.getItem('activePlaylistId');
        this.apiService.addSongToPlaylist(playlistId, song).subscribe(
            response => {
                this.setSongData(response);
            },
            error => {
                alert('Please open a playlist before adding a song');
                console.log(error);
            }
        );
    }

    pollPlaylist() {
    	var playlistId = localStorage.getItem('activePlaylistId');
    	if (playlistId != null) {
    		this.getPlaylist(playlistId);
            this.highlightCurrentlyPlayingSong();
    	}
    }

    getPlaylist(playlistId) {
        this.apiService.getPlaylist(playlistId, undefined).subscribe(
          (response: Array<Object>) => {
            // response returns access code then a list of songs
            var nameAccessCode = response.shift();
            this.playlistName = nameAccessCode['Name'];
            this.playlistCode = nameAccessCode['AccessCode'];
            localStorage.setItem('activePlaylistId', playlistId);
            this.songData = response;
            this.getPlacedVotes();
            this.setSongData(response);
          },
          error => {
            console.log(error);
          }
        );
    }

    deleteSong(songSpotifyId) {
        var playlistId = localStorage.getItem('activePlaylistId');
        this.apiService.deleteSongFromPlaylist(playlistId, songSpotifyId).subscribe(
            response => {
                this.setSongData(response);
            },
            error => {
                console.log(error);
            }
        );
    }

    upvoteSong(dbSongId: string, content) {
        var playlistVote = 'playlist:' + localStorage.getItem('activePlaylistId') + dbSongId;
        if(localStorage.getItem(playlistVote) === null || localStorage.getItem(playlistVote) == 'downvoted') {
            this.apiService.upvoteSong(dbSongId).subscribe(
                response => this.setSongData(response),
                error => console.log(error)
            );
            if (localStorage.getItem(playlistVote) === null) {
        		localStorage.setItem(playlistVote, 'upvoted');
        		this.setVoteState(dbSongId, 1);
        	} else {
        		localStorage.removeItem(playlistVote);
        		this.setVoteState(dbSongId, 0);
        	}
        } 
        /** 
        else {
            this.modalService.open(content, {ariaLabelledBy: 'modal-basic-title'})
        }
        **/

    }

    downvoteSong(dbSongId: string, content) {
        var playlistVote = 'playlist:' + localStorage.getItem('activePlaylistId') + dbSongId;
        if(localStorage.getItem(playlistVote) === null || localStorage.getItem(playlistVote) == 'upvoted') {
            this.apiService.downvoteSong(dbSongId).subscribe(
                response => this.setSongData(response),
                error => console.log(error)
            );
            if (localStorage.getItem(playlistVote) === null) {
        		localStorage.setItem(playlistVote, 'downvoted');
        		this.setVoteState(dbSongId, -1);
        	} else {
        		localStorage.removeItem(playlistVote);
        		this.setVoteState(dbSongId, 0);
        	}
        } 
        /**
        else {
            this.modalService.open(content, {ariaLabelledBy: 'modal-basic-title'})
        }
        **/
    }

    setVoteState(dbSongId: string, voteValue) {
    	if (voteValue == 1) {
    		this.upvotes.set(dbSongId, true);
    		this.downvotes.set(dbSongId, false);
    	} else if (voteValue == -1) {
    		this.upvotes.set(dbSongId, false);
    		this.downvotes.set(dbSongId, true);
    	} else {
    		this.upvotes.set(dbSongId, false);
    		this.downvotes.set(dbSongId, false);
    	}
    }

    getPlacedVotes() {
    	for (var song in this.songData) {
    		var songId = this.songData[song]['id'];
    		var songVoteKey = 'playlist:' + localStorage.getItem('activePlaylistId') + songId;
    		var voteState = localStorage.getItem(songVoteKey);
    		if (voteState == 'upvoted') {
    			this.setVoteState(songId, 1);
    		} else if (voteState == 'downvoted') {
    			this.setVoteState(songId, -1);
    		} else {
    			this.setVoteState(songId, 0);
    		}
    	}
    }

    setSongData(data: any) {
        this.songData = data;
        // get voting record for current user
        data.forEach(song => {
            let vote = localStorage.getItem('playlist:' + localStorage.getItem('activePlaylistId') + song.id);
            if (vote)
                this.votes[song.id] = vote.charAt(0);

        });
    }

    highlightCurrentlyPlayingSong() {
        var currentlyPlayingSongId = localStorage.getItem('currentlyPlayingSongId');
        if (this.lastPlayedSongId != currentlyPlayingSongId) {
            this.playStates.set(this.lastPlayedSongId, false);
            this.playStates.set(currentlyPlayingSongId, true);
            this.lastPlayedSongId = currentlyPlayingSongId;
        }
    }
}