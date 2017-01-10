import {Component, OnInit, ViewEncapsulation, HostBinding} from '@angular/core';
import { ActivatedRoute } from "@angular/router";
import { ServersService } from "../servers.service";
import { games } from "../game/game.component";
import { Game } from "../game/game";
import {Server} from "../server";

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

  constructor( private route: ActivatedRoute) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = params['id'];
    });
    this.game = this.games.filter(game => game.id === this.id)[0];
  }

}
