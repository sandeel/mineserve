import {Component} from "@angular/core";
import {Router} from "@angular/router";
import { UserRegistrationService, CognitoCallback, LoggedInCallback, UserLoginService }
from "../../service/cognito.service";

export class RegistrationUser {
    name: string;
    email: string;
    password: string;
}
/**
 * This component is responsible for displaying and controlling
 * the registration of the user.
 */
@Component({
  selector: 'app-register',
  templateUrl: './registration.html'
})
export class RegisterComponent implements CognitoCallback, LoggedInCallback {
  registrationUser: RegistrationUser;
  router: Router;
  errorMessage: string;

  constructor(
    public userRegistration: UserRegistrationService,
    router: Router,
    private userLoginService: UserLoginService
  ){
    this.router = router;
    this.onInit();
  }

  onInit() {
    this.registrationUser = new RegistrationUser();
    this.errorMessage = null;
    this.userLoginService.isAuthenticated(this);
  }

  onRegister() {
      this.errorMessage = null;
      this.userRegistration.register(this.registrationUser, this);
  }

  cognitoCallback(message: string, result: any) {
      if (message != null) { //error
          this.errorMessage = message;
          console.log("result: " + this.errorMessage);
      } else { //success
          //move to the next step
          console.log("redirecting");
          this.router.navigate(['users/confirmRegistration', result.user.username]);
      }
  }

  isLoggedIn(message:string, isLoggedIn:boolean) {
    if (isLoggedIn){
      this.router.navigate(['/']);
    }
  }
}
