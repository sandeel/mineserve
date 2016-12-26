import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './common/auth.guard';

const routes: Routes = [
  {
    path: '',
    loadChildren: 'app/home/home.module#HomeModule'
  },
  {
    path: 'servers',
    loadChildren: 'app/servers/servers.module#ServersModule'
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
