import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './common/auth.guard';
import {HomeComponent} from "./home/home.component";

const routes: Routes = [
  {
    path: 'users',
    loadChildren: 'app/users/users.module#UsersModule'
  },
	{ path: '', redirectTo: 'home', pathMatch: 'full' },
  {
    path: 'home',
    component: HomeComponent
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
