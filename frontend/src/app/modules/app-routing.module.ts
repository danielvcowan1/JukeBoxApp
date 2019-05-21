import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { StartComponent } from '../components/start/start.component';

const routes: Routes = [
  { path: '', component: StartComponent },
  { path: 'host', loadChildren: './host-client.module#HostClientModule' },
  { path: 'guest', loadChildren: './guest-client.module#GuestClientModule' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
