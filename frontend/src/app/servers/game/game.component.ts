import { Component, OnInit, HostBinding } from '@angular/core';
import { Game } from "./game";
import {StepsService} from "../../steps/steps-service";

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.css'
  ]
})
export class GameComponent implements OnInit {
  games: Game[];
  constructor(private stepsService: StepsService) {
  }
  ngOnInit() {
    this.stepsService.increaseStep(0);
    this.games = games;
  }
}

export const games: Game[] = [
  new Game("1", "Minecraft"),
  new Game("2", "Ark"),
  new Game("3", "DayZ"),
  new Game("4", "Factorio")
]
