import { Component, Injectable } from '@angular/core';
import { SpotifyAPIService } from 'src/app/services/spotifyAPI.service';

/**
 * Host user interface
 */
@Component({
  selector: 'host-layout',
  templateUrl: './host-layout.component.html',
  styleUrls: ['./host-layout.component.css']
})

export class HostLayoutComponent {

  private userAuthenticated: boolean = false;
  private obtainingToken: boolean = false;
  private displayName: string;

  
  constructor(private spotifyAPIService: SpotifyAPIService) { }

  ngOnInit() {
    //this.elementRef.nativeElement.ownerDocument.body.style.backgroundColor = 'yourColor';

    let urlParams = new URLSearchParams(window.location.search);
    let code = urlParams.get('code');
    if (code)
      this.obtainingToken = true;
      this.spotifyAPIService.obtainAccessToken(code).subscribe(
        response => {
          let userId = response['id'];
          let accessToken = response['token'];
          this.displayName = response['display_name'];
          if (userId && accessToken) {
            this.userAuthenticated = true;
            this.obtainingToken = false;
            localStorage.setItem('spotifyId', userId);
            this.spotifyAPIService.setUserIdAccessToken(userId, accessToken);
          }
        },
        error => {
          // error most likely indicates that the user is not authenticated
          console.log(error);
          this.userAuthenticated = false;
          this.obtainingToken = false;
        },
        () => { }
      );
  }

  /**
   * Bound to "Spotify Login" button click action.
   */
  private performSpotifyLogin() {
    window.open(this.spotifyAPIService.getLoginURL(), '_self');
          //.addEventListener("beforeunload", function() {}.bind(this));
  }  
}