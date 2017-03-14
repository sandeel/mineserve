import datetime
import jwt
import base64
import six
import struct
import requests
import pytz
import stripe
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from werkzeug.local import LocalProxy
from mineserve.models import Server
from contextlib import contextmanager
from functools import wraps

from flask import request, jsonify, abort, make_response, _app_ctx_stack, appcontext_pushed, g
from flask_cors import cross_origin

from mineserve import application, stripe_keys
from mineserve.models import User
from mineserve.models import Server


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

        client_id = "gJv54phVRi5DcleXXy2ipeCM3J2FmGG5"
        client_secret = "r-eKjoNIhsf2491X7YYJRYd0_S7uYPIBRlDXfDkZrihJmMeHkOk278UJggwGv91Z"
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
    user = str(_app_ctx_stack.top.current_user)

    topped_up_message = None
    promo_code_applied=False
    invalid_promo_code=False
    error_message=None

    server = next(Server.query(id))

    if request.method == 'POST':

        if data['stripeToken']:

            amount = Server.prices[server.size]

            customer = stripe.Customer.create(
                card=data['stripeToken'],
                metadata={ "server_id": id }
            )

            charge = stripe.Charge.create(
                customer=customer.id,
                amount=amount,
                currency='usd',
                description='Flask Charge',
                metadata={"server_id": server.id}
            )

            if charge['status'] == "succeeded":

                server.expiry_date = server.expiry_date + datetime.timedelta(days=30)

                server.save()

                topped_up_message = "Topped up by 30 days."

            else:
                error_message = "Payment failed"

        elif request.form['promo-code']:
            server = Server.query.filter_by(id=server_id).first()
            if server.apply_promo_code(request.form['promo-code']):
                promo_code_applied=True
            else:
                invalid_promo_code=True

    if (datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - server.creation_date).seconds < 3600:
        new_server = True
    else:
        new_server = False

    td = server.expiry_date - datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

    return jsonify(time_remaining=str(days)+' days, '+str(hours)+' hours, '+str(minutes)+' minutes',
            id=id,
            ip=server.ip,
            key=stripe_keys['publishable_key'],
            status=server.status,
            new_server=True,
            topped_up_message=topped_up_message,
            beta=application.config['BETA'],
            invalid_promo_code=invalid_promo_code,
            size=server.size,
            price='{0:.02f}'.format(float(Server.prices[server.size]) / 100.0),
            error_message=error_message,
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


print("Fetching JWKS")
r = requests.get("https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_HMLKJ8toC/.well-known/jwks.json")
jwks = r.json()

pems = {}

for jwk in jwks['keys']:
    exponent = base64_to_long(jwk['e'])
    modulus = base64_to_long(jwk['n'])
    numbers = RSAPublicNumbers(exponent, modulus)
    public_key = numbers.public_key(backend=default_backend())
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    pems[jwk['kid']] = pem

print("JWKs converted to PEMS")


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





@application.route("/api/0.1/testing/servers", methods=["GET", "POST", "DELETE"])
def test_servers():

    test_return_json="""{
      "servers": [
        {
            "creation_date": "2017-03-12 16:17:58.001031+00:00",
            "expiry_date": "2017-03-12 17:36:07.623360+00:00",
            "id": "8f2ea3e7-9ba6-4040-91b0-1fb06d69e681",
            "ip": "Unknown",
            "name": "Jurassic Ark",
            "status": "stub_resource",
            "time_remaining": "0 days, 1 hours, 0 minutes",
            "user": "auth0|58bf293e61d8c359422f7154",
            "type": "ark_server",
            "size": "large"
        },
        {
            "creation_date": "2017-03-12 16:17:58.001031+00:00",
            "expiry_date": "2017-03-12 17:36:07.623360+00:00",
            "id": "8f2ea3e7-9ba6-4040-91b0-1fb06d69e681",
            "ip": "Unknown",
            "name": "Jurassic Ark 2",
            "status": "stub_resource",
            "time_remaining": "0 days, 1 hours, 0 minutes",
            "user": "auth0|58bf293e61d8c359422f7154",
            "type": "ark_server",
            "size": "large"
        }
      ]
    }
    """

    return test_return_json

