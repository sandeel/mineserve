"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var core_1 = require('@angular/core');
var cognito_service_1 = require("../service/cognito.service");
var ddb_service_1 = require("../service/ddb.service");
var LoginComponent = (function () {
    function LoginComponent(router, userLoginService, http) {
        this.router = router;
        this.userLoginService = userLoginService;
        this.http = http;
        this.loading = false;
        this.msgs = [];
        this.mfaShow = false;
    }
    LoginComponent.prototype.ngOnInit = function () {
        this.errorMessage = null;
        console.log("Checking if the user is already authenticated. If so, then redirect to the secure site");
        this.userLoginService.isAuthenticated(this);
    };
    LoginComponent.prototype.redirect = function () {
        this.router.navigate(['/dashboard']);
    };
    LoginComponent.prototype.onLogin = function () {
        this.loading = true;
        this.msgs = [];
        if (this.username == null || this.username == "") {
            this.msgs.push({ severity: 'warn', summary: 'Login failed', detail: "Username is required" });
            this.loading = false;
            return false;
        }
        if (this.password == null || this.password == "") {
            this.msgs.push({ severity: 'warn', summary: 'Login failed', detail: "Password is required" });
            this.loading = false;
            return false;
        }
        this.userLoginService.authenticate(this.username, this.password, this, this);
    };
    LoginComponent.prototype.isLoggedIn = function (message, isLoggedIn) {
        if (isLoggedIn)
            this.router.navigate(['/']);
    };
    LoginComponent.prototype.cognitoCallback = function (message, result) {
        if (message != null) {
            this.errorMessage = message;
            console.log("result: " + this.errorMessage);
            if (message == "Invalid code or auth state for the user.") {
                this.loading = false;
                this.msgs.push({ severity: 'error', summary: 'Login failed', detail: "Invalid MFA code." });
            }
            else {
                this.loading = false;
                this.msgs.push({ severity: 'error', summary: 'Login failed', detail: message });
            }
        }
        else {
            localStorage.setItem('currentUser', this.username);
            console.log(result);
            console.log("getAccessToken", this.userLoginService.cognitoUtil.getAccessToken(new AccessTokenCallback()));
            this.router.navigate(['/']);
        }
    };
    LoginComponent.prototype.getMFA = function (callback) {
        this.loading = false;
        this.mfaShow = true;
        this.templateMFACallback = callback;
    };
    LoginComponent.prototype.submitMFA = function () {
        if (this.mfaCode != null && this.mfaCode != "") {
            this.loading = true;
            this.templateMFACallback.mfaCallback(this.mfaCode, this.templateMFACallback);
        }
        else {
            this.msgs = [];
            this.msgs.push({ severity: 'warn', summary: 'MFA Invalid', detail: "MFA must be 6 digits" });
        }
    };
    LoginComponent = __decorate([
        core_1.Component({
            selector: 'app-login',
            templateUrl: 'users.component.html',
            styleUrls: ['users.component.css', '../loading/loading.component.css'],
            providers: [cognito_service_1.UserLoginService, ddb_service_1.DynamoDBService, cognito_service_1.CognitoUtil]
        })
    ], LoginComponent);
    return LoginComponent;
}());
exports.LoginComponent = LoginComponent;
var LogoutComponent = (function () {
    function LogoutComponent(router, userService) {
        this.router = router;
        this.userService = userService;
        this.userService.isAuthenticated(this);
    }
    LogoutComponent.prototype.isLoggedIn = function (message, isLoggedIn) {
        if (isLoggedIn) {
            this.userService.logout();
            this.router.navigate(['/']);
        }
        localStorage.clear();
        this.router.navigate(['/']);
    };
    LogoutComponent = __decorate([
        core_1.Component({
            selector: 'app-login',
            template: '',
            providers: [cognito_service_1.UserLoginService, ddb_service_1.DynamoDBService, cognito_service_1.CognitoUtil]
        })
    ], LogoutComponent);
    return LogoutComponent;
}());
exports.LogoutComponent = LogoutComponent;
var AccessTokenCallback = (function () {
    function AccessTokenCallback() {
    }
    AccessTokenCallback.prototype.callback = function () { };
    AccessTokenCallback.prototype.callbackWithParam = function (result) {
        localStorage.setItem('accessToken', result);
    };
    return AccessTokenCallback;
}());
exports.AccessTokenCallback = AccessTokenCallback;
