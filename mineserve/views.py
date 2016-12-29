from mineserve import application, db, stripe_keys
from flask import request, render_template, jsonify, abort, make_response
from flask_security import login_required, roles_accepted
from mineserve.models import User
from flask_security.utils import encrypt_password
from mineserve.models import Server
from flask import redirect
import datetime
import jwt
from functools import wraps
import base64
import six
import struct
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import requests
from flask import _request_ctx_stack as stack
from werkzeug.local import LocalProxy

current_user = LocalProxy(lambda: getattr(stack.top, 'current_user', None))

#mcpe
from mcpe.mcpeserver import MCPEServer

#ark
from ark.arkserver import ArkServer

@application.route("/server/<server_id>/properties", methods=["GET"])
def server_properties(server_id):
    server = Server.query.filter_by(id=server_id).first()
    response = make_response(server.properties.generate_file())
    response.headers["content-type"] = "text/plain"
    response.content_type = "text/plain"
    return response

@application.route("/server/<server_id>", methods=["GET","POST"])
def server(server_id):

    topped_up_message = None
    promo_code_applied=False
    invalid_promo_code=False
    error_message=None

    if request.method == 'POST':

        if request.form.get('stripeToken', None):

            server = Server.query.filter_by(id=server_id).first()

            amount = Server.prices[server.size]

            customer = stripe.Customer.create(
                card=request.form['stripeToken'],
                metadata={ "server_id": server_id }
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

                db.session.commit()

                topped_up_message = "Topped up by 30 days."

            else:
                error_message = "Payment failed"

        elif request.form['promo-code']:
            server = Server.query.filter_by(id=server_id).first()
            if server.apply_promo_code(request.form['promo-code']):
                promo_code_applied=True
            else:
                invalid_promo_code=True

    server = Server.query.filter_by(id=server_id).first()

    if (datetime.datetime.now() - server.creation_date).seconds < 3600:
        new_server = True
    else:
        new_server = False

    td = server.expiry_date - datetime.datetime.now()
    days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

    return render_template('server.html',
            time_remaining=str(days)+' days, '+str(hours)+' hours, '+str(minutes)+' minutes',
            id=server.id,
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

def rcon(server, command):
    Popen(['/opt/mcrcon/mcrcon/mcrcon', '-H', server.private_ip, '-P', '33775', '-p', 'password', command])

@application.route("/admin", methods=["GET","POST"])
@roles_accepted('admin')
def main_admin_page():
    pass

@application.route("/admin/messenger", methods=["GET","POST"])
@roles_accepted('admin')
def messenger():
    if request.method == "GET":
        return render_template('messenger.html')
    elif request.method == "POST":
        if request.form['message'] and request.form['server_id']:
            server = Server.query.filter_by(id=request.form['server_id']).first()
            message = request.form['message']
            rcon(server, "say "+message)
            return render_template('messenger.html')

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


def _jwt_required():
    auth_header = request.headers.get('Authorization', None)

    if not auth_header:
        return

    allowed_auth_header_prefixes = ['jwt']

    parts = auth_header.split()

    if parts[0].lower() not in allowed_auth_header_prefixes:
        raise JWTError('Invalid JWT header', 'Unsupported authorization type')
    elif len(parts) == 1:
        raise JWTError('Invalid JWT header', 'Token missing')
    elif len(parts) > 2:
        raise JWTError('Invalid JWT header', 'Token contains spaces')

    token = parts[1]

    print("JWT token = "+token)

    kid = jwt.get_unverified_header(token)['kid']

    print("Pem for kid is "+str(pems[kid]))

    try:
        payload = jwt.decode(token,pems[kid],algorithms=['RS256'],audience="7oa9ir0uf69e54krmhkrcno0g6")
        stack.top.current_user = payload['cognito:username']
    except:
        abort(403)


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


def jwt_required():
    """View decorator that requires a valid JWT token to be present in the request
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            _jwt_required()
            return fn(*args, **kwargs)
        return decorator
    return wrapper


@application.route("/api/0.1/users", methods=["GET","POST"])
@jwt_required()
def users():

    if request.args.get('id'):
        user = User(request.args.get('username'))
        return jsonify(users = user.serialize())


@application.route("/api/0.1/servers", methods=["GET", "POST", "DELETE"])
@jwt_required()
def servers():

    if request.method == "DELETE":

        if application.config['STUB_AWS_RESOURCES']:
            abort(200)

        data = request.get_json(force=True)

        server_to_delete = Server.query.filter_by(id=data['id']).first()

        db.session.delete(server_to_delete)
        db.session.commit()

    if request.method == "POST":

        data = request.get_json(force=True)

        user = current_user

        if not user:
            return abort(400)

        size = data['size']
        new_server = globals()[data['type']](
                            name=data['server_name'],
                            size = size,
                            user=user)

        new_server.properties.max_players = Server.max_players[new_server.size]

        db.session.add(new_server)

        db.session.commit()

        return jsonify(new_server.serialize())

    if current_user:
        return jsonify(servers=[s.serialize() for s in Server.query.filter_by(user=current_user)])

