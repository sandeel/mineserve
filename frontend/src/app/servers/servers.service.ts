import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import {Http, URLSearchParams, Headers, Response} from '@angular/http';

import { Server } from './server';

@Injectable()
export class ServersService {

  private url = 'app/servers/servers.json';
  private headers = new Headers();
  private servers: Observable<Server[]>
  constructor(private http: Http) {
  }
  getServers(): Observable<Server[]> {
    let params = new URLSearchParams();
    // params.set('callback', 'JSONP_CALLBACK');
    return this.http.get(this.url)
      .map(res => res.json());
  }
}
