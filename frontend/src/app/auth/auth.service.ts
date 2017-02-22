import { Injectable }      from '@angular/core';
import { tokenNotExpired } from 'angular2-jwt';
import { Router } from '@angular/router';

// Avoid name not found warnings
let Auth0Lock = require('auth0-lock').default;


@Injectable()
export class Auth {
  // Configure Auth0
  lock = new Auth0Lock('gJv54phVRi5DcleXXy2ipeCM3J2FmGG5', 'gameserve.eu.auth0.com', {
    theme: {
      primaryColor: "#01303F"
    },
    languageDictionary: {
    title: "GameServe"
  }
  });
  userProfile: Object;

  constructor(public router: Router) {
    this.userProfile = JSON.parse(localStorage.getItem('profile'));

    // Add callback for the Lock `authenticated` event
    this.lock.on("authenticated", (authResult) => {
      localStorage.setItem('id_token', authResult.idToken);

      // Fetch profile information
      this.lock.getProfile(authResult.idToken, (error, profile) => {
        if (error) {
          // Handle error
          alert(error);
          return;
        }
        console.log(profile);
        localStorage.setItem('profile', JSON.stringify(profile));
        this.userProfile = profile;
      });
    });
  }

  public login() {
    // Call the show method to display the widget.
    this.lock.show();
  }

  public authenticated() {
    // Check if there's an unexpired JWT
    // This searches for an item in localStorage with key == 'id_token'
    return tokenNotExpired();
  }

  public logout() {
    // Remove token from localStorage
    localStorage.removeItem('id_token');
    this.router.navigate(['/']);
  }
}