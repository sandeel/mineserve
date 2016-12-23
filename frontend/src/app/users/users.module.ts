import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoginComponent, LogoutComponent } from './users.component';

import { UsersRoutingModule } from './users-routing.module';
import { FormsModule } from "@angular/forms";
import { LoadingModule } from "../loading/loading.module";
import { MessagesModule } from "primeng/primeng";

@NgModule({
  imports: [
    CommonModule,
    UsersRoutingModule,
    FormsModule,
    LoadingModule,
    MessagesModule
  ],
  declarations: [
    LoginComponent,
    LogoutComponent,
  ],
  exports: [  ]
})
export class UsersModule { }
