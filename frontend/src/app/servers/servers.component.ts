import { Component, OnInit } from '@angular/core';
import { ServersService} from "./servers.service";
import { Server } from './server';

@Component({
  selector: 'app-servers',
  templateUrl: './servers.component.html',
  styleUrls: ['./servers.component.css'],
  providers: [ ServersService ]
})
export class ServersComponent implements OnInit {

  constructor(private serversService: ServersService ) { }
  private servers: Server[];
  selectedServer: Server;
  displayDialog: boolean;
  errorMessage: string;

  ngOnInit() {
    this.serversService.getServers()
      .subscribe(
        servers => this.servers = servers,
        error =>  this.errorMessage = <any>error
      );
  }

  selectServer(server: Server) {
    this.selectedServer = server;
    this.displayDialog = true;
  }
  onDialogHide() {
    this.selectedServer = null;
  }
}
