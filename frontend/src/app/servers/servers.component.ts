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
        error =>  this.router.navigate(["/users/logout"])
      );
  }

  selectServer(event) {
    this.selectedServer = event.data;
    this.router.navigate(['/servers/', this.selectedServer.id]);
  }
}