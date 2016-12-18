from mineserve import application, db, mail, stripe_keys
from flask import request, render_template, jsonify, abort
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user, roles_accepted
from mineserve.models import User
from flask_mail import Message
from flask_security.utils import encrypt_password
import flask_login
from mineserve.models import Server, user_datastore
from flask import Flask, redirect
import datetime

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

@application.route("/server/<server_id>/dashboard", methods=["GET","POST"])
@login_required
def dashboard(server_id):
    server = Server.query.filter_by(id=server_id).first()
    if (server.owner != current_user):
        return abort(403)

    if request.method == "POST":
        # server name
        server.properties.server_name = request.form['name']


        # message of the day`
        server.properties.motd = request.form['motd']


        # mobs
        #if request.form.get('mobs'):
            #server.properties.spawn_mobs = "on"
        #else:
            #server.properties.spawn_mobs = "off"

        db.session.commit()

        server.reboot_instance()

        return redirect("/server/"+server_id)


    else:

        return render_template('dashboard.html',
                               id = server.id,
                               name = server.properties.server_name,
                               motd = server.properties.motd,
                               mobs = server.properties.spawn_mobs,
                               )

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


@application.route("/api/0.1/users", methods=["GET","POST"])
def users():

    if request.method == "POST":

        data = request.get_json(force=True)

        if user_datastore.get_user(data['email']):
            return render_template('landing_page.html', form_error="That email address has already been taken.")
        else:
            # create the user
            # password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
            encrypted_password = encrypt_password(data['password'])

            user_datastore.create_user(email=data['email'], password=encrypted_password)

            db.session.commit()

            user = user_datastore.get_user(data['email'])

            return jsonify(user.serialize())

    if request.args.get('id'):
        user = User.query.filter_by(id=request.args.get('id')).first()
        return jsonify(users = user.serialize())
    return jsonify(users=[u.serialize() for u in User.query.all()])


@application.route("/api/0.1/servers", methods=["GET","POST","DELETE"])
def servers():

    if request.method == "DELETE":

        data = request.get_json(force=True)

        server_to_delete = Server.query.filter_by(id=data['id']).first()

        db.session.delete(server_to_delete)
        db.session.commit()

    if request.method == "POST":

        data = request.get_json(force=True)

        user = User.query.filter_by(id=data['user_id']).first()

        if not user:
            return abort(400)

        #size = data['size']
        size = 'micro'
        new_server =  globals()[data['type']](
                            name=data['server_name'],
                            size = size,
                            user=user)

        new_server.properties.max_players = Server.max_players[new_server.size]

        db.session.add(new_server)

        db.session.commit()

        return jsonify(new_server.serialize())

    if request.args.get('user'):
        user = User.query.filter_by(id=request.args.get('user')).first()
        return jsonify(servers=[s.serialize() for s in user.servers])

    return jsonify(servers=[s.serialize() for s in Server.query.all()])
