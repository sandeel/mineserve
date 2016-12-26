import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ServersComponent } from './servers.component';

const serversRoutes: Routes = [
  {
    path: '',
    component: ServersComponent
  }
];
@NgModule({
  imports: [ RouterModule.forChild(serversRoutes) ],
  exports: [ RouterModule ]
})
export class ServersRoutingModule {}
