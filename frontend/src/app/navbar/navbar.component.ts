import { Component, OnInit } from '@angular/core';
import { ConfirmationService } from "primeng/components/common/api";
import { Router } from "@angular/router";
import { Auth } from '../auth/auth.service';


@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit  {
  constructor(private confirmationService: ConfirmationService,
              private router: Router,
              private auth: Auth
               ) {  }

  private loggedIn: Boolean = false;
  public username: string = localStorage.getItem('currentUser');

  ngOnInit() {
    
  }

  confirmLogout(event) {
    event.preventDefault();
    this.confirmationService.confirm({
      header: 'Logout',
      icon: 'fa fa-sign-out',
      message: 'Are you sure that you want to logout?',
      accept: () => {
        this.auth.logout();
      }
    });
  }
}
