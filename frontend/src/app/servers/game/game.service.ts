import { Injectable } from '@angular/core';
import {Game} from "./game";

@Injectable()
export class GameService {
  games:Game[] = [
    new Game("1", "Minecraft")
  ];
  constructor() { }
  getGame(id: string){
    for (let game of this.games){
      if (game.id == id){
        return game
      }
    }
  }
}
