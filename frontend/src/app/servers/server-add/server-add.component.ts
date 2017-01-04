import { Component, OnInit } from '@angular/core';
import {ServersService} from "../servers.service";

@Component({
  selector: 'app-server-add',
  templateUrl: './server-add.component.html',
  styleUrls: ['./server-add.component.css'],
  providers: [ ServersService ]
})
export class ServerAddComponent implements OnInit {
  res: string;
  constructor(private serversService: ServersService) { }

  ngOnInit() {
  }
  addServer(){
    this.serversService.addServer().subscribe(data => this.res = data);
  }
}
