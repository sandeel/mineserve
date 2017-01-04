import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ServersComponent } from './servers.component';
import { NavbarModule } from '../navbar/navbar.module';
import { DataTableModule, TabViewModule } from 'primeng/primeng';
import { ServersRoutingModule } from "./servers-routing.module";
import { ServerDetailComponent } from './server-detail/server-detail.component';
import { LoadingModule } from "../loading/loading.module";
import { FooterModule } from "../footer/footer.module";
import { ServerAddComponent } from './server-add/server-add.component';


@NgModule({
  imports: [
    CommonModule,
    NavbarModule,
    DataTableModule,
    ServersRoutingModule,
    LoadingModule,
    TabViewModule,
    FooterModule
  ],
  declarations: [
    ServersComponent,
    ServerDetailComponent,
    ServerAddComponent
  ]
})
export class ServersModule { }
