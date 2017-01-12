import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ServersService } from "../servers.service";
import { Message, MenuItem } from "primeng/components/common/api";
import { StepsService } from "../../steps/steps-service";
import { Step } from "../../steps/step";

@Component({
  selector: 'app-server-add',
  templateUrl: './server-add.component.html',
  styleUrls: [ './server-add.component.css' ],
  providers: [ ServersService ],
  encapsulation: ViewEncapsulation.None
})
export class ServerAddComponent implements OnInit {
  res: string;
  msgs: Message[] = [];
  activeIndex: number = 1;
  steps: Step[];
  private items: MenuItem[];

  constructor(private serversService: ServersService, private stepsService: StepsService) { }

  ngOnInit() {
    this.stepsService.getSteps().subscribe(val => this.steps = val);
    this.items = [{
      label: 'Personal',
      command: (event: any) => {
        this.activeIndex = 0;
        this.msgs.length = 0;
        this.msgs.push({severity:'info', summary:'First Step', detail: event.item.label});
      }
    },
      {
        label: 'Seat',
        command: (event: any) => {
          this.activeIndex = 1;
          this.msgs.length = 0;
          this.msgs.push({severity:'info', summary:'Seat Selection', detail: event.item.label});
        }
      },
      {
        label: 'Payment',
        command: (event: any) => {
          this.activeIndex = 2;
          this.msgs.length = 0;
          this.msgs.push({severity:'info', summary:'Pay with CC', detail: event.item.label});
        }
      },
      {
        label: 'Confirmation',
        command: (event: any) => {
          this.activeIndex = 3;
          this.msgs.length = 0;
          this.msgs.push({severity:'info', summary:'Last Step', detail: event.item.label});
        }
      }
    ];
  }
  addServer(){
    this.serversService.addServer().subscribe(data => this.res = data);
  }
}
