import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import { Http } from '@angular/http';
import { GetHeaders } from '../common/headers';

import { Server } from './server';

@Injectable()
export class ServersService {
  constructor( private http: Http, private getHeaders: GetHeaders ) {
  }
  getServers(): Observable<Server[]> {
      let url = 'http://52.51.32.218:8000/api/0.1/servers';
    return this.http.get(url, {
      headers: this.getHeaders.getHeaders()
    }).map(res => res.json());
  }
  getServerDetail(serverId: string): Observable<Server> {
    let url = 'http://192.168.0.109:5000/server/' + serverId + "/properties";
    return this.http.get(url, {
      headers: this.getHeaders.getHeaders()
    }).map(res => res.json());
  }
}
