import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { LoginComponent, LogoutComponent } from './users.component';
import { RegisterComponent } from "../auth/register/registration.component";
import { RegistrationConfirmationComponent } from "../auth/confirm/confirmRegistration.component";
import {ResendCodeComponent} from "../auth/resend/resendCode.component";
import {ForgotPassword2Component, ForgotPasswordStep1Component} from "../auth/forgot/forgotPassword.component";

const userRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'login' },
  { path: 'login', component: LoginComponent },
  { path: 'logout', component: LogoutComponent },
  { path: 'confirmRegistration/:username', component: RegistrationConfirmationComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'resendCode', component: ResendCodeComponent},
  { path: 'forgotPassword/:email', component: ForgotPassword2Component},
  { path: 'forgotPassword', component: ForgotPasswordStep1Component},
];
@NgModule({
  imports: [ RouterModule.forChild(userRoutes) ],
  exports: [ RouterModule ]
})
export class UsersRoutingModule {}
