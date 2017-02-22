import { Injectable } from '@angular/core';
import { Router, CanActivate, CanLoad, CanActivateChild } from '@angular/router';
import { Auth } from '../auth/auth.service';

@Injectable()
export class AuthGuard implements CanActivate, CanActivateChild, CanLoad {
  errorMessage: string;
  constructor(private router: Router, private auth: Auth) {}

  canActivate() {
    return this.auth.authenticated();
  }

  canActivateChild() {
    return this.auth.authenticated();
  }

  canLoad(){
    return this.auth.authenticated();
  }

  isLoggedIn(message:string, isLoggedIn:boolean) {
    if (isLoggedIn)
      return true;
    else {
      this.errorMessage = message;
      console.log("result: " + this.errorMessage);
      console.log("Navigating to users/login");
      this.router.navigate(['/users/login']);
      return false;
    }
  }
}
