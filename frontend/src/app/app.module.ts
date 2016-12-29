import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule, JsonpModule } from '@angular/http';

import { AuthGuard } from './common/auth.guard';
import { UserLoginService, CognitoUtil } from "./service/cognito.service";
import { DataListModule, DialogModule } from 'primeng/primeng';

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from './app.component';
import { TokenComponent } from './token/token.component';

@NgModule({
  declarations: [
    AppComponent,
    TokenComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    JsonpModule,
    AppRoutingModule,
    DataListModule,
    DialogModule
  ],
  providers: [ AuthGuard, UserLoginService, CognitoUtil ],
  bootstrap: [AppComponent]
})
export class AppModule { }
