import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule, JsonpModule } from '@angular/http';

import { AuthGuard } from './common/auth.guard';
import { UserLoginService, CognitoUtil } from "./service/cognito.service";

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from './app.component';
import { HomeComponent } from "./home/home.component";
import { NavbarModule } from "./navbar/navbar.module";
import {ServersComponent} from "./servers/servers.component";

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    ServersComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    JsonpModule,
    AppRoutingModule,
    NavbarModule
  ],
  providers: [ AuthGuard, UserLoginService, CognitoUtil ],
  bootstrap: [AppComponent]
})
export class AppModule { }
