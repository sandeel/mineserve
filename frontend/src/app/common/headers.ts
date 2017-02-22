import { Headers } from '@angular/http';
import { Injectable, OnInit } from "@angular/core";

@Injectable()
export class GetHeaders{
  constructor() { }

  getHeaders() {
    let contentHeaders = new Headers();
    contentHeaders.append('Accept', 'application/json');
    contentHeaders.append('Content-Type', 'application/json');
    contentHeaders.append('Authorization', 'JWT ' + localStorage.getItem("authToken"));
    return contentHeaders;
  }
}
