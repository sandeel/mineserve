import { Component, OnInit } from '@angular/core';
import { StepsService} from "../../steps/steps-service";
import { ServerAddService} from "../server-add/server-add.service";
import { ServerAdd} from "../server-add/server-add";
import {ServersService} from "../servers.service";

@Component({
  selector: 'app-server-confirm',
  templateUrl: './server-confirm.component.html',
  styleUrls: ['./server-confirm.component.css']
})
export class ServerConfirmComponent implements OnInit {
  private server: ServerAdd;
  addRes: string = "";
  constructor(private steps: StepsService, private serverAddService: ServerAddService,
              private serversService: ServersService
  ) { }

  ngOnInit() {
    this.steps.increaseStep(3);
    this.serverAddService.getServer().subscribe(res => {
      this.server = res;
      console.log(res);
      this.serversService.addServer(res.name, res.size).subscribe(res=> this.addRes = res);
    });
  }

}
