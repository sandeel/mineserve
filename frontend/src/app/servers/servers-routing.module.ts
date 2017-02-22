import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ServersComponent } from './servers.component';
import { ServerDetailComponent} from "./server-detail/server-detail.component";
import { GameComponent } from "./game/game.component";
import { ServerAddComponent} from "./server-add/server-add.component";
import { ServerPayComponent} from "./server-pay/server-pay.component";
import {ServerConfirmComponent} from "./server-confirm/server-confirm.component";

const serversRoutes: Routes = [
  {
    path: '',
    component: ServersComponent
  },
  {
    path: 'add',
    component: ServerAddComponent,
    children: [
      {
        path: 'pay',
        component: ServerPayComponent
      },
      {
        path: 'confirm',
        component: ServerConfirmComponent
      },
      {
        path: ':id',
        component: ServerDetailComponent
      },
      {
        path: '',
        pathMatch: 'full',
        component: GameComponent
      }
    ]
  }
];
@NgModule({
  imports: [ RouterModule.forChild(serversRoutes) ],
  exports: [ RouterModule ]
})
export class ServersRoutingModule {}
