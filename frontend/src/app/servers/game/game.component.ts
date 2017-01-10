import { Component, OnInit, HostBinding } from '@angular/core';
import { Game } from "./game";

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.css'
  ]
})
export class GameComponent implements OnInit {
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
