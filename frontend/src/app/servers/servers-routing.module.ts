import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ServersComponent } from './servers.component';
import {ServerDetailComponent} from "./server-detail/server-detail.component";

const serversRoutes: Routes = [
  {
    path: '',
    component: ServersComponent
  },
  {
    path: ':id',
    component: ServerDetailComponent
  }
];
@NgModule({
  imports: [ RouterModule.forChild(serversRoutes) ],
  exports: [ RouterModule ]
})
export class ServersRoutingModule {}
