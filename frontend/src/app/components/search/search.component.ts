import { Component, Output, EventEmitter, Input } from '@angular/core';
import { ViewChild, ElementRef } from '@angular/core';
import { SpotifyAPIService } from 'src/app/services/spotifyAPI.service';
import { CommonModule } from "@angular/common";

@Component({
    selector: 'search',
    templateUrl: './search.component.html',
    styleUrls: ['./search.component.css']
})
export class SearchComponent {

	@ViewChild('searchInput') input:ElementRef; 
	@Output() addSongEvent = new EventEmitter();
	@Input() guestSearch: boolean
	
	searchHidden: boolean = false;
	searchResponse: any;
	displayedResults: any;
	defaultLimit: number = 10;
	currentLimit: number = 10;
	maxLimit: number = 50;

	constructor (private spotifyAPIService: SpotifyAPIService) {
        this.searchResponse = [];
        this.displayedResults = []
    }

	/**
	 * Bound to search button click action.
	 */
	private searchSpotify () {
		let searchText = this.input.nativeElement.value;
		let searchType = 'all';
        let spotifyId = this.spotifyAPIService.getUserId();

    	this.spotifyAPIService.querySpotifyApi(spotifyId, searchText, searchType).subscribe(
			response => {
				this.searchResponse = response;
				this.displayedResults = this.searchResponse.slice(0, this.defaultLimit);
				this.searchHidden = false;
			},
			error => {
				console.log(error);
				// handle error
			}
		);
	}

	private loadMoreResults() {
		if(this.currentLimit <= this.maxLimit){
			this.currentLimit += 10;
			this.displayedResults = this.searchResponse.slice(0, this.currentLimit);
		}
	}

	private resultsLoaded(){
		return !(this.searchResponse.length === 0);
	}

	private searchSpotifyAsGuest () {
		let searchText = this.input.nativeElement.value;
		let searchType = 'all';
        let playlistId = localStorage.getItem('activePlaylistId');

    	this.spotifyAPIService.querySpotifyApiAsGuest(playlistId, searchText, searchType).subscribe(
			response => {
				this.searchResponse = response;
				this.displayedResults = this.searchResponse.slice(0, this.defaultLimit);
				this.searchHidden = false;
			},
			error => {
				console.log(error);
				// handle error
			}
		);
	}
	  
	/**
	 * Use this function to emit a song selection to the playlist component.
     * (Tells the playlist component to add a song)
	 */
	private emitSongSelection(addSongEvent: Event, song: any) {
		this.addSongEvent.emit(song);
	}
}