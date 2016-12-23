import { NgModule } from '@angular/core';
import  {RouterModule, Routes, PreloadAllModules } from '@angular/router';

const routes: Routes = [
	{ path: '', redirectTo: '/users/login', pathMatch: 'full' },
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
  // providers: [ PreloadSelectedModules ]
})
export class AppRoutingModule {}
