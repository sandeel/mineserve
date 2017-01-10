import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoginComponent, LogoutComponent } from './users.component';

import { UsersRoutingModule } from './users-routing.module';
import { FormsModule } from "@angular/forms";
import { LoadingModule } from "../loading/loading.module";
import { MessagesModule } from "primeng/primeng";
import { RegisterComponent } from "../auth/register/registration.component";
import { RegistrationConfirmationComponent } from "../auth/confirm/confirmRegistration.component";
import { ResendCodeComponent } from "../auth/resend/resendCode.component";
import { ForgotPasswordStep1Component, ForgotPassword2Component } from "../auth/forgot/forgotPassword.component";

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
    RegisterComponent,
    RegistrationConfirmationComponent,
    ResendCodeComponent,
    ForgotPasswordStep1Component,
    ForgotPassword2Component
  ],
  exports: [  ]
})
export class UsersModule { }
