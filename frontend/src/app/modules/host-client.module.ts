import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HostLayoutComponent } from '../components/host-layout/host-layout.component';
import { HostRouting } from '../routing/host-client.routing';
import { SharedComponentsModule } from './shared-components.module';
import { SongPlayerComponent } from '../components/song-player/song-player.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

/**
 * Module for running the host client user interface
 */
@NgModule({
  declarations: [
    HostLayoutComponent,
    SongPlayerComponent
  ],
  imports: [
    CommonModule,
    HostRouting,
    SharedComponentsModule,
    NgbModule
  ],
  // exports: [
  //   HostLayoutComponent
  // ]
})
export class HostClientModule { }
