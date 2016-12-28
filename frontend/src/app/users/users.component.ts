import { Component, OnInit } from '@angular/core';
import { Router } from "@angular/router";
import { Http } from '@angular/http';
import { Message } from 'primeng/primeng';
import { CognitoCallback, Callback, UserLoginService, CognitoUtil, LoggedInCallback } from "../service/cognito.service";

@Component({
  selector: 'app-login',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css'],
  providers: [ UserLoginService, CognitoUtil ]
})
export class LoginComponent implements CognitoCallback, OnInit, LoggedInCallback {
  username: string;
  password: string;
  errorMessage:string;
  loading: boolean = false;
  msgs: Message[] = [];
  mfaCode: string;
  templateMFACallback: any;
  mfaShow: boolean = false;

  constructor( private router: Router,
               private userLoginService: UserLoginService,
               public http: Http ) { }

  ngOnInit() {
    this.errorMessage = null;
    console.log("Checking if the user is already authenticated. If so, then redirect to the secure site");
    this.userLoginService.isAuthenticated(this);
  }

  redirect(){
    this.router.navigate(['/dashboard']);
  }

  onLogin(){
    this.loading = true;
    this.msgs = [];
    if (this.username == null || this.username == ""){
      this.msgs.push({severity:'warn', summary:'Login failed', detail:"Username is required"});
      this.loading = false;
      return false;
    }
    if (this.password == null || this.password == ""){
      this.msgs.push({severity:'warn', summary:'Login failed', detail:"Password is required"});
      this.loading = false;
      return false;
    }
    this.userLoginService.authenticate(this.username, this.password, this, this);
  }

  isLoggedIn(message:string, isLoggedIn:boolean) {
    if (isLoggedIn){
      console.log("YES");
      this.router.navigate(['/']);
    }
  }

  cognitoCallback(message:string, result:any) {
    if (message != null) { //error
      this.errorMessage = message;
      console.log("result: " + this.errorMessage);

      if (message == "Invalid code or auth state for the user."){
        this.loading = false;
        this.msgs.push({severity:'error', summary:'Login failed', detail:"Invalid MFA code."});
      }
      else{
        this.loading = false;
        this.msgs.push({severity:'error', summary:'Login failed', detail:message});
      }
    } else { //success
      localStorage.setItem('currentUser', this.username);
      localStorage.setItem('authToken', result.accessToken.jwtToken);
      this.router.navigate(['/']);
    }
  }

  getMFA(callback: any){
    this.loading = false;
    this.mfaShow = true;
    this.templateMFACallback = callback;
  }

  submitMFA(){
    if (this.mfaCode != null && this.mfaCode != "" ){
      this.loading = true;
      this.templateMFACallback.mfaCallback(this.mfaCode, this.templateMFACallback);
    }
    else {
      this.msgs = [];
      this.msgs.push({severity:'warn', summary:'MFA Invalid', detail:"MFA must be 6 digits"});
    }
  }
}

@Component({
  selector: 'app-login',
  template: '',
  providers: [ UserLoginService, CognitoUtil ]
})
export class LogoutComponent implements LoggedInCallback {

  constructor(public router:Router, public userService:UserLoginService) {
    this.userService.isAuthenticated(this)
  }

  isLoggedIn(message:string, isLoggedIn:boolean) {
    if (isLoggedIn) {
      this.userService.logout();
      this.router.navigate(['/']);
    }
    localStorage.clear();
    this.router.navigate(['/']);
  }
}


export class AccessTokenCallback implements Callback {
  constructor() { }
  callback() { }
  callbackWithParam(result) {
    localStorage.setItem('accessToken', result);
  }
}
