import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";
import { ServersService } from "../servers.service";
import { games } from "../game/game.component";
import { Game } from "../game/game";
import { Server} from "../server";
import { StepsService } from "../../steps/steps-service";
import { ServerAddService} from "../server-add/server-add.service";

@Component({
  selector: 'app-server-detail',
  templateUrl: './server-detail.component.html',
  styleUrls: ['./server-detail.component.css'],
  providers: [ ServersService ],
  encapsulation: ViewEncapsulation.None
})
export class ServerDetailComponent implements OnInit {

  id: string;
  game: Game;
  games = games;

  server: Server;
  sizes = ['micro', 'large'];

  selectedSize: string;
  serverName: string;

  constructor( private route: ActivatedRoute, private router: Router,
               stepsService: StepsService, private serverAddService: ServerAddService ) {
    stepsService.increaseStep(1);
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = params['id'];
    });
    this.game = this.games.filter(game => game.id === this.id)[0];
  }

  goToPayment(value){
    console.log(value);
    console.log("Going to payment");
    this.serverAddService.setServer(value.name, value.size);
    this.router.navigate(['/servers/add/pay', {someProperty:"SomeValue"}]);
  }
}
