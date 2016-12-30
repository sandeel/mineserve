export class Server {
  id: string;
  type: string;
  expiry_date: string;
  creation_date: string;
  user: string;
  name: string;
  ip: string;
  status: string;

  constructor(id: string, type: string, expiry_date: string, creation_date: string, user: string, name: string){
    this.id = id;
    this.type = type;
    this.expiry_date = expiry_date;
    this.creation_date = creation_date;
    this.user = user;
    this.name = name;
  }
}
