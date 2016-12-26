import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ServersComponent } from './servers.component';
import { NavbarModule } from '../navbar/navbar.module';
import { DataListModule, DialogModule } from 'primeng/primeng';
import {ServersRoutingModule} from "./servers-routing.module";

@NgModule({
  imports: [
    CommonModule,
    NavbarModule,
    DataListModule,
    DialogModule,
    ServersRoutingModule
  ],
  declarations: [
    ServersComponent
  ]
})
export class ServersModule { }
