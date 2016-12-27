import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ServersComponent } from './servers.component';
import { NavbarModule } from '../navbar/navbar.module';
import { DataTableModule } from 'primeng/primeng';
import {ServersRoutingModule} from "./servers-routing.module";
import { ServerDetailComponent } from './server-detail/server-detail.component';

@NgModule({
  imports: [
    CommonModule,
    NavbarModule,
    DataTableModule,
    ServersRoutingModule
  ],
  declarations: [
    ServersComponent,
    ServerDetailComponent
  ]
})
export class ServersModule { }
