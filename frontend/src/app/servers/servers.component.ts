import {Component, OnInit, Pipe, PipeTransform} from '@angular/core';
import {ServersService} from "./servers.service";
import {Server } from './server';

@Component({
  selector: 'app-servers',
  templateUrl: './servers.component.html',
  styleUrls: ['./servers.component.css'],
  providers: [ ServersService ]
})
export class ServersComponent implements OnInit {

  constructor(private serversService: ServersService ) { }
  private servers: Server[];
  errorMessage: string;

  ngOnInit() {
    this.serversService.getServers()
      .subscribe(
        servers => this.servers = servers,
        error =>  this.errorMessage = <any>error
      );
  }
  logLog(){
    console.log(this.servers);
  }
}
