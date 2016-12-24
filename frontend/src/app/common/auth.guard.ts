import { Injectable } from '@angular/core';
import {Router, CanActivate, CanLoad, CanActivateChild} from '@angular/router';
import {LoggedInCallback, UserLoginService} from "../service/cognito.service";



@Injectable()
export class AuthGuard implements CanActivate, CanActivateChild, CanLoad, LoggedInCallback {
  errorMessage: string;
  constructor(private router: Router, private userService: UserLoginService) {}

  canActivate() {
    this.userService.isAuthenticated(this);
    return true;
  }

  canActivateChild() {
    this.userService.isAuthenticated(this);
    return true;
  }

  canLoad(){
    this.userService.isAuthenticated(this);
    return true;
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
