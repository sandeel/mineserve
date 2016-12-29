import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-token',
  templateUrl: './token.component.html',
  styleUrls: ['./token.component.css']
})
export class TokenComponent implements OnInit {
  private token: string = localStorage.getItem("authToken");
  constructor() { }

  ngOnInit() {
  }

}
