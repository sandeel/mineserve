import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './common/auth.guard';
import {HomeComponent} from "./home/home.component";
import {ServersComponent} from "./servers/servers.component";

const routes: Routes = [
  {
    path: '',
    component: HomeComponent
  },
  {
    path: 'servers',
    component: ServersComponent
  },
  {
    path: 'users',
    loadChildren: 'app/users/users.module#UsersModule'
  }
];

@NgModule({
  imports: [
    RouterModule.forRoot(
      routes
      , { useHash: true }
    )
  ],
  exports: [
    RouterModule
  ],
  providers: [ AuthGuard ]
})
export class AppRoutingModule {}
