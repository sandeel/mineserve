import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './common/auth.guard';
import { TokenComponent } from "./token/token.component";

const routes: Routes = [
  {
    path: '',
    loadChildren: 'app/home/home.module#HomeModule'
  },
  {
    path: 'servers',
    loadChildren: 'app/servers/servers.module#ServersModule',
    canLoad: [ AuthGuard ]
  },
  {
    path: 'token',
    component: TokenComponent
  }
];

@NgModule({
  imports: [
    RouterModule.forRoot(
      routes
      , { useHash: false }
    )
  ],
  exports: [
    RouterModule
  ],
  providers: [ AuthGuard ]
})
export class AppRoutingModule {}
