import { Injectable } from '@angular/core';
import { BehaviorSubject} from "rxjs";
import { ServerAdd} from "./server-add";

@Injectable()
export class ServerAddService {
  private _server: BehaviorSubject<ServerAdd> = new BehaviorSubject<ServerAdd>(null);
  public server: ServerAdd = new ServerAdd("", "");
  constructor(  ) {
    this._server.next(this.server);
  }
  getServer() {
    return this._server.asObservable();
  }
  public setServer(name: string, size: string){
    this.server.name = name;
    this.server.size = size;
    this._server.next(this.server);
  }
}
