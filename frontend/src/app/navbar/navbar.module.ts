import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NavbarComponent } from './navbar.component';
import { ConfirmDialogModule, ConfirmationService } from 'primeng/primeng';
@NgModule({
  imports: [
    CommonModule,
    RouterModule,
    ConfirmDialogModule
  ],
  declarations: [NavbarComponent],
  providers: [ ConfirmationService ],
  exports: [
    NavbarComponent
  ]
})
export class NavbarModule { }
