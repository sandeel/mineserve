import datetime
import jwt
import base64
import six
import struct
import requests
import pytz
import stripe
from mineserve.models import Server
from contextlib import contextmanager
from functools import wraps
from flask import request, jsonify, abort, _app_ctx_stack, appcontext_pushed
from mineserve import application
from mineserve.models import User
from mineserve.models import topup_packages


@contextmanager
def user_set(application, user):
    def handler(sender, **kwargs):
        _app_ctx_stack.top.current_user = user
    with appcontext_pushed.connected_to(handler, application):
        yield


# This is the new auth function
# I am pretty sure it uses the client secret and id to verify the token
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if hasattr(_app_ctx_stack.top, 'current_user'):
            return f(*args, **kwargs)

        client_id =  application.config['AUTH0_CLIENT_ID']
        client_secret = application.config['AUTH0_CLIENT_SECRET']
        auth = request.headers.get('Authorization', None)
        if not auth:
            return handle_error({'code': 'authorization_header_missing',
                                'description':
                                    'Authorization header is expected'}, 401)

        parts = auth.split()

        if parts[0].lower() != 'bearer':
            return handle_error({'code': 'invalid_header',
                                'description':
                                    'Authorization header must start with'
                                    'Bearer'}, 401)
        elif len(parts) == 1:
            return handle_error({'code': 'invalid_header',
                                'description': 'Token not found'}, 401)
        elif len(parts) > 2:
            return handle_error({'code': 'invalid_header',
                                'description': 'Authorization header must be'
                                 'Bearer + \s + token'}, 401)

        token = parts[1]
        try:
            payload = jwt.decode(
                token,
                client_secret,
                audience=client_id
            )
        except jwt.ExpiredSignature:
            return handle_error({'code': 'token_expired',
                                'description': 'token is expired'}, 401)
        except jwt.InvalidAudienceError:
            return handle_error({'code': 'invalid_audience',
                                'description': 'incorrect audience, expected: '
                                 + client_id}, 401)
        except jwt.DecodeError:
            return handle_error({'code': 'token_invalid_signature',
                                'description':
                                    'token signature is invalid'}, 401)
        except Exception:
            return handle_error({'code': 'invalid_header',
                                'description': 'Unable to parse authentication'
                                 ' token.'}, 400)

        _app_ctx_stack.top.current_user = payload['sub']
        return f(*args, **kwargs)

    return decorated


@application.route("/api/0.1/servers/<id>/topup", methods=["POST"])
@requires_auth
def topup(id):
    data = request.get_json(force=True)

    server = next(Server.query(id))

    topup_package = str(data['topup_package'])
    days_to_top_up = topup_packages[topup_package]['days']
    amount_to_charge = int(topup_packages[topup_package]['charge'])

    if data['stripeToken']:
        customer = stripe.Customer.create(
            card=data['stripeToken'],
            metadata={ "server_id": id }
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount_to_charge,
            currency='usd',
            description='Flask Charge',
            metadata={"server_id": server.id}
        )

        if charge['status'] == "succeeded":
            server.expiry_date = (server.expiry_date +
                                  datetime.timedelta(days=days_to_top_up))
            server.save()

    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    td = server.expiry_date - now
    days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

    return jsonify(time_remaining=str(days)+' days, ' +
                   str(hours)+' hours, ' +
                   str(minutes)+' minutes',
                   id=id
                   )


# set up jwt
def intarr2long(arr):
    return int(''.join(["%02x" % byte for byte in arr]), 16)


def base64_to_long(data):
    if isinstance(data, six.text_type):
        data = data.encode("ascii")

    # urlsafe_b64decode will happily convert b64encoded data
    _d = base64.urlsafe_b64decode(bytes(data) + b'==')
    return intarr2long(struct.unpack('%sB' % len(_d), _d))


class JWTError(Exception):
    def __init__(self, error, description, status_code=401, headers=None):
        self.error = error
        self.description = description
        self.status_code = status_code
        self.headers = headers

    def __repr__(self):
        return 'JWTError: %s' % self.error

    def __str__(self):
        return '%s. %s' % (self.error, self.description)


@application.route("/api/0.1/users", methods=["GET","POST"])
@requires_auth
def users():

    if request.args.get('id'):
        user = User(request.args.get('username'))
        return jsonify(users = user.serialize())


@application.route("/api/0.1/servers", methods=["GET", "POST", "DELETE"])
@requires_auth
def servers():
    if request.method == "POST":
        data = request.get_json(force=True)
        user = str(_app_ctx_stack.top.current_user)

        if not user:
            return abort(400)

        size = data['size']
        # give 1 hour and 5 minutes free
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        now_plus_1_hours = now + datetime.timedelta(minutes=65)
        new_server = Server(name=data['name'],
                            size=size,
                            user=user,
                            expiry_date=now_plus_1_hours,
                            region=data['region'])
        new_server.save()

        return jsonify(new_server.serialize())

    if _app_ctx_stack.top.current_user == 'unauthenticated_user':
        return jsonify("")

    if _app_ctx_stack.top.current_user:
        return jsonify(servers=[s.serialize() for s in Server.user_index.query(str(_app_ctx_stack.top.current_user))])


@application.route("/api/0.1/servers/<id>", methods=["GET", "POST", "DELETE"])
@requires_auth
def server(id):
    server = next(Server.query(id))

    if server.user != str(_app_ctx_stack.top.current_user):
        abort(403)

    if request.method == "GET":
        return jsonify(server.serialize())

    elif request.method == "POST":
        if application.config['STUB_AWS_RESOURCES']:
            abort(200)

        server.restart()

        return jsonify(servers=[s.serialize() for s in Server.user_index.query(str(_app_ctx_stack.top.current_user))])

    elif request.method == "DELETE":
        server.delete()

        return jsonify(servers=[s.serialize() for s in Server.user_index.query(str(_app_ctx_stack.top.current_user))])


#
# Next three functions were for testing Auth 0
#


def handle_error(error, status_code):
    resp = jsonify(error)
    resp.status_code = status_code
    return resp


@application.route("/secured/ping", methods=["GET"])
@requires_auth
def secured_ping():
    print(_app_ctx_stack.top.current_user)
    # Getting the token from the headers
    auth = request.headers.get('Authorization', None)
    # Splitting token ['bearer', 'xxxxxxxxxxxxx']
    # Auth 0 tokens have to start with bearer, so we use the second part
    parts = auth.split()
    # This url just returns a load of user information with the given token passed
    url = "https://gameserve.eu.auth0.com/tokeninfo"
    print(requests.get(url, params={"id_token": parts[1]}).text)
    return "All good. You only get this message if you're authenticated"


