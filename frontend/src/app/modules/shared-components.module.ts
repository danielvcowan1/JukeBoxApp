import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SearchComponent } from '../components/search/search.component';
import { PlaylistDisplayComponent } from '../components/playlist-display/playlist-display.component';
import { PlaylistComponent } from '../components/playlist/playlist.component';

/*
This is where we will put components that we use in both
the host client and guest client. This will be just
a Search component, plus any other components we decide
to use in both the desktop and mobile clients.
 */

@NgModule({
  declarations: [
    SearchComponent,
    PlaylistDisplayComponent,
    PlaylistComponent
  ],
  imports: [
    CommonModule
  ],
  exports: [
    SearchComponent,
    PlaylistDisplayComponent,
    PlaylistComponent
  ]
})
export class SharedComponentsModule { }
