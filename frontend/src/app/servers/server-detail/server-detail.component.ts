import {Component, OnInit, ViewEncapsulation, HostBinding} from '@angular/core';
import { ActivatedRoute } from "@angular/router";
import { ServersService } from "../servers.service";
import { games } from "../game/game.component";
import { slideInLeftAnimation } from "../../animations";
import { Game } from "../game/game";

@Component({
  selector: 'app-server-detail',
  templateUrl: './server-detail.component.html',
  styleUrls: ['./server-detail.component.css'],
  providers: [ ServersService ],
  encapsulation: ViewEncapsulation.None,
  animations: [ slideInLeftAnimation ]
})
export class ServerDetailComponent implements OnInit {
  @HostBinding('@routeAnimation') routeAnimation = true;
  @HostBinding('style.display')   display = 'block';
  @HostBinding('style.position')  position = 'absolute';
  @HostBinding('style.width')  width = '100%';

  id: string;
  game: Game;
  games = games;
  constructor( private route: ActivatedRoute) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = params['id'];
    });
    this.game = this.games.filter(game => game.id === this.id)[0];
  }

}
