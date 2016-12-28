import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from "@angular/router";
import { ServersService } from "../servers.service";
import { Server } from "../server";

@Component({
  selector: 'app-server-detail',
  templateUrl: './server-detail.component.html',
  styleUrls: ['./server-detail.component.css'],
  providers: [ ServersService ]
})
export class ServerDetailComponent implements OnInit {
  id: string;
  server: Server;
  constructor(private route: ActivatedRoute, private serversService: ServersService) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = params['id'];
    });
    this.serversService.getServerDetail(this.id).subscribe(server => this.server = server);
  }

}
