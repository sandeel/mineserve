import { Component, OnInit } from '@angular/core';
import { UserLoginService, LoggedInCallback } from "../service/cognito.service";

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit, LoggedInCallback {
  constructor(private userLoginService: UserLoginService) {  }
  private loggedIn: Boolean = false;
  public username: string = localStorage.getItem('currentUser');
  ngOnInit() {
    this.userLoginService.isAuthenticated(this);
  }
  isLoggedIn(message:string, isLoggedIn:boolean) {
    if (isLoggedIn)
      this.loggedIn = true;
  }
}
