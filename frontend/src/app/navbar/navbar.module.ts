import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NavbarComponent } from './navbar.component';
import { ConfirmDialogModule, ConfirmationService } from 'primeng/primeng';
import { Auth } from '../auth/auth.service';

@NgModule({
  imports: [
    CommonModule,
    RouterModule,
    ConfirmDialogModule
  ],
  declarations: [NavbarComponent],
  providers: [ ConfirmationService, Auth ],
  exports: [
    NavbarComponent
  ]
})
export class NavbarModule { }
