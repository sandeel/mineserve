from mineserve.models import Server
from mineserve.models import LogEntry
import datetime
import time
import boto3
from mineserve import application
from mineserve import db
import syslog

syslog.openlog(facility=syslog.LOG_LOCAL5)

def process_server(server_id):
    server = Server.query.filter_by(id=server_id).first()

    log_entry = ('Server '+server.id+' phoned home.')

    td = server.expiry_date - datetime.datetime.now()

    seconds_left = td.total_seconds()
    hours_left = seconds_left // 3600

    server_message = ''

    if server.expiry_date < datetime.datetime.now():

        log_entry += ('Server '+server.id+' expired, terminating...')

        try:
            client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
            response = client.terminate_instances(
                InstanceIds=[
                    server.instance_id,
                ]
            )
        except Exception as e:
            print(e)

    elif hours_left < 1:
        server_message = "WARNING. Server will be terminated in less than an hour unless topped-up. All data will be lost."
    elif hours_left < 2:
        server_message = "WARNING. Server will be terminated in two hours unless topped-up. All data will be lost."
    elif hours_left < 3:
        server_message = "WARNING. Server will be terminated in three hours unless topped-up. All data will be lost."
    elif hours_left < 4:
        server_message ="WARNING. 4 hours credit remaining on this server."
    elif hours_left < 5:
        server_message ="WARNING. 5 hours credit remaining on this server."
    elif hours_left < 24:
        server_message ="WARNING. 24 hours credit remaining on this server."

    if server_message:
        rcon(server, 'say '+server_message)

    else:
        log_entry += ('No server message sent for server '+server.id)

    db.session.add(LogEntry(log_entry))

    db.session.commit()

    return

sleep_time = 5
while (True):
    for server in Server.query.all():
        print("Processing "+server.id)
        process_server(server.id)
    syslog.syslog("Sleeping for "+str(sleep_time)+" seconds")
    time.sleep(sleep_time)

