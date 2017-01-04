import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ServersService } from "./servers.service";
import { Server } from './server';
import { Router } from '@angular/router';

@Component({
  selector: 'app-servers',
  templateUrl: './servers.component.html',
  styleUrls: ['./servers.component.css'],
  providers: [ ServersService ],
  encapsulation: ViewEncapsulation.None,
})
export class ServersComponent implements OnInit {

  constructor( private serversService: ServersService, private router: Router ) { }
  private servers: Server[];
  selectedServer: Server;
  errorMessage: string;

  ngOnInit() {
    this.serversService.getServers()
      .subscribe(
        servers => this.servers = servers['servers'],
        error =>  this.errorMessage = error
      );
  }

  restartServer(server: Server){
    alert("Server restarting. Please wait a few minutes for it to come back up.");

    this.serversService.restartServer(server.id).subscribe(
        servers => this.servers = servers['servers'],
        error => this.errorMessage = <any>error
    );
  }

  deleteServer(server: Server){
    this.serversService.deleteServer(server.id).subscribe(res => this.errorMessage = res);
    console.log("Deleting Server: " + server.id);
  }
}
