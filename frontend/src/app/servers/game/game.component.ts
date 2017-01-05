import { Component, OnInit, HostBinding } from '@angular/core';
import { slideInRightAnimation } from "../../animations";
import { Game } from "./game";

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.css'],
  animations: [ slideInRightAnimation ]
})
export class GameComponent implements OnInit {
  @HostBinding('@routeAnimation') routeAnimation = true;
  @HostBinding('style.display')   display = 'block';
  @HostBinding('style.position')  position = 'absolute';
  @HostBinding('style.width')  width = '100%';
  games: Game[];
  constructor() {
  }
  ngOnInit() {
    this.games = games;
  }
}

export const games: Game[] = [
  new Game("1", "Minecraft"),
  new Game("2", "Ark"),
  new Game("3", "DayZ"),
  new Game("4", "Factorio")
]
