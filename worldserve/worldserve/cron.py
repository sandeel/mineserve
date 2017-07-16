from servers.models import Server
import datetime


def check_servers():
    for server in Server.objects.all():
        time_now = datetime.datetime.now(datetime.timezone.utc)
        if (server.expiry_date > time_now):
            server.delete()
            print(server.id + ' terminated.')
