import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ServersComponent } from './servers.component';
import { NavbarModule } from '../navbar/navbar.module';

@NgModule({
  imports: [
    CommonModule,
    NavbarModule
  ],
  declarations: [
    ServersComponent
  ]
})
export class ServersModule { }
