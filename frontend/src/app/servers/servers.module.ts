import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ServersComponent } from './servers.component';
import { DataTableModule, TabViewModule } from 'primeng/primeng';
import { ServersRoutingModule } from "./servers-routing.module";
import { ServerDetailComponent } from './server-detail/server-detail.component';
import { LoadingModule } from "../loading/loading.module";
import { ServerAddComponent } from './server-add/server-add.component';
import { GameComponent } from './game/game.component';


@NgModule({
  imports: [
    CommonModule,
    DataTableModule,
    ServersRoutingModule,
    LoadingModule,
    TabViewModule,
  ],
  declarations: [
    ServersComponent,
    ServerDetailComponent,
    ServerAddComponent,
    GameComponent
  ]
})
export class ServersModule { }
