from servers.models import Server
import datetime
from django.conf import settings
from django.core.mail import send_mail


def check_servers():
    print("Checking servers for expiry")
    for server in Server.objects.all():
        time_now = datetime.datetime.now(datetime.timezone.utc)
        if (time_now > server.expiry_date):
            print('Terminating ' + server.id)
            server.delete()

            email_subject = getattr(settings, "TERMINATION_EMAIL_SUBJECT", None)
            email_body = getattr(settings, "TERMINATION_EMAIL_BODY", None)
            email_from = getattr(settings, "EMAIL_SENDER", None)
            email_to = [server.user.email,]

            send_mail(
                email_subject,
                email_body,
                email_from,
                email_to,
                fail_silently=False,
            )
