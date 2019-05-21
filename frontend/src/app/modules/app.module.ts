import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from '../components/app/app.component';
import { StartComponent } from '../components/start/start.component';
import { HttpClientModule } from '@angular/common/http';
import { ApiService } from '../services/api.service';
import { NavbarComponent } from '../components/navbar/navbar.component';

@NgModule({
  declarations: [
    AppComponent,
    StartComponent,
    NavbarComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
  ],
  providers: [ApiService],
  bootstrap: [AppComponent]
})
export class AppModule { }
