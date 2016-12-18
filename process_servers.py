from mineserve.models import Server
import datetime
import time
from mineserve import db
import syslog

syslog.openlog(facility=syslog.LOG_LOCAL5)

def process_server(server_id):
    server = Server.query.filter_by(id=server_id).first()

    td = server.expiry_date - datetime.datetime.now()

    seconds_left = td.total_seconds()
    hours_left = seconds_left // 3600

    if server.expiry_date < datetime.datetime.now():

        try:
            db.session.delete(server)
            db.session.commit()
        except Exception as e:
            print(e)

    else:
        print("Server "+server.id+" has "+str(hours_left)+" hours, "+str(seconds_left)+ "seconds left.")

    db.session.commit()

    return

sleep_time = 60
while (True):
    for server in Server.query.all():
        print("Processing "+server.id)
        process_server(server.id)
    syslog.syslog("Sleeping for "+str(sleep_time)+" seconds")
    time.sleep(sleep_time)

