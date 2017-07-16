from servers.models import Server
import datetime


def check_servers():
    print("Checking servers for expiry")
    for server in Server.objects.all():
        time_now = datetime.datetime.now(datetime.timezone.utc)
        if (time_now > server.expiry_date):
            server.delete()
            print(server.id + ' terminated.')
