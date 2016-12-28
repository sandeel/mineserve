import { Headers } from '@angular/http';
import { Callback, UserLoginService } from "../service/cognito.service";
import { Injectable, OnInit } from "@angular/core";

@Injectable()
export class GetHeaders{
  constructor(private userLoginService: UserLoginService) { }

  getHeaders() {
    let contentHeaders = new Headers();
    contentHeaders.append('Accept', 'application/json');
    contentHeaders.append('Content-Type', 'application/json');
    contentHeaders.append('Authorization', 'JWT ' + localStorage.getItem("authToken"));
    return contentHeaders;
  }
}
