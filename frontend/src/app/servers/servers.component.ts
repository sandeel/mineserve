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
    this.serversService.restartServer(server.id).subscribe(error => this.errorMessage = <any>error);
    alert("Server restarting. Please wait a few minutes for it to come back up.");
  }

  deleteServer(server: Server){
    console.log("Deleting Server: " + server.id);
  }
}
