import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import {Http, URLSearchParams, Headers, Response} from '@angular/http';

import { Server } from './server';

@Injectable()
export class ServersService {

  private url = 'http://192.168.0.108:5000/api/0.1/servers';
  private headers = new Headers();
  private servers: Observable<Server[]>
  constructor(private http: Http) {
  }
  getServers(): Observable<Server[]> {
    let params = new URLSearchParams();
    return this.http.get(this.url)
      .map(res => res.json());
  }
}
