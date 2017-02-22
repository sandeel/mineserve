import { Component, OnInit } from '@angular/core';
import { StepsService} from "../../steps/steps-service";
import {Router, ActivatedRoute} from "@angular/router";

@Component({
  selector: 'app-server-pay',
  templateUrl: './server-pay.component.html',
  styleUrls: ['./server-pay.component.css']
})
export class ServerPayComponent implements OnInit {

  constructor( private steps: StepsService, private router: Router, public route: ActivatedRoute) { }

  ngOnInit() {
    this.steps.increaseStep(2);
    this.route.params.subscribe(res => {
      console.log(res['someProperty']);
    });
  }
  goToConfirmation(){
    this.router.navigate(['/servers/add/confirm']);
  }

}
