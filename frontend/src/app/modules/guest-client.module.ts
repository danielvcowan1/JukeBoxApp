import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GuestLayoutComponent } from '../components/guest-layout/guest-layout.component';
import { GuestRouting } from '../routing/guest-client.routing';
import { SharedComponentsModule } from './shared-components.module';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

/**
 * Module for running the guest client user interface
 */
@NgModule({
  declarations: [
    GuestLayoutComponent
  ],
  imports: [
    CommonModule,
    GuestRouting,
    SharedComponentsModule,
    NgbModule
  ],
})
export class GuestClientModule { }
