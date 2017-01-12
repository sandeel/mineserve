import { NgModule } from '@angular/core';

import { CommonModule } from '@angular/common';
import { ServersComponent } from './servers.component';
import { DataTableModule, TabViewModule, StepsModule } from 'primeng/primeng';
import { ServersRoutingModule } from "./servers-routing.module";
import { ServerDetailComponent } from './server-detail/server-detail.component';
import { LoadingModule } from "../loading/loading.module";
import { ServerAddComponent } from './server-add/server-add.component';
import { GameComponent } from './game/game.component';
import { NavbarModule } from "../navbar/navbar.module";
import {FormsModule} from "@angular/forms";
import {StepsService} from "../steps/steps-service";


@NgModule({
  imports: [
    CommonModule,
    DataTableModule,
    FormsModule,
    ServersRoutingModule,
    LoadingModule,
    TabViewModule,
    NavbarModule,
    StepsModule
  ],
  declarations: [
    ServersComponent,
    ServerDetailComponent,
    ServerAddComponent,
    GameComponent
  ],
  providers: [StepsService]
})
export class ServersModule { }
