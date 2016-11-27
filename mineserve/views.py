from mineserve import application, db, mail, stripe_keys
from flask import request, render_template
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user, roles_accepted
from mineserve import models
from flask_mail import Message
from flask.ext.security.utils import encrypt_password
import flask.ext.login as flask_login
from mineserve.models import Server
from flask import Flask, redirect
import datetime

@application.route("/", methods=["GET", "POST"])
def landing_page():
    if request.method == "POST":

            # validate entered data
            if not request.form['email']:
                return render_template('landing_page.html', form_error="Please enter your email address.", beta_test=application.config['BETA'])
            if not request.form['server_name']:
                return render_template('landing_page.html', form_error="Please enter a name for your server.", beta_test=application.config['BETA'])
            if not request.form['minecraft_name']:
                return render_template('landing_page.html', form_error="Please enter your Minecraft name.", beta_test=application.config['BETA'])
            if not request.form['password']:
                return render_template('landing_page.html', form_error="Please enter a password.", beta_test=application.config['BETA'])

            # if beta need promo code
            if application.config['BETA']:
                if not request.form['promo-code']:
                        return render_template('landing_page.html', form_error="Promo code required.", beta_test=application.config['BETA'])
                else:
                    if not new_server.apply_promo_code(request.form['promo-code']):
                        return render_template('landing_page.html', form_error="Invalid Promo Code.", beta_test=application.config['BETA'])

                if User.query.filter_by(email=request.form['email']).first():
                    return render_template('landing_page.html', form_error="That user already has a beta server.", beta_test=application.config['BETA'])


            db.session.add(models.LogEntry('Customer has requested a new server'))
            msg = Message(subject="Customer has requested a new server",
                  body="Email address: "+request.form['email'],
                  sender="adventureservers@kolabnow.com",
                  recipients=["adventureservers@kolabnow.com"])
            mail.send(msg)

            if models.user_datastore.get_user(request.form['email']):
                return render_template('landing_page.html', form_error="That email address has already been taken.")
            else:
                # create the user
                # password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
                encrypted_password = encrypt_password(request.form['password'])

                models.user_datastore.create_user(email=request.form['email'], password=encrypted_password)

                db.session.commit()

                user = models.user_datastore.get_user(request.form['email'])
                flask_login.login_user(user)

                # send reset password
                #`send_reset_password_instructions(user)

                # if server doesn't exist create it
                #size = request.form['size']
                size = 'micro'
                new_server = Server(op=request.form['minecraft_name'],
                                    server_name=request.form['server_name'],
                                    size = size)

                new_server.op=request.form['minecraft_name']
                server_id = new_server.id

                user.servers.append(new_server)

                new_server.properties.max_players = Server.max_players[new_server.size]

                db.session.add(new_server)

                db.session.commit()

                return redirect('/server/'+server_id)
    else:
        return render_template('landing_page.html', beta_test=application.config['BETA'])


@application.route("/server_data", methods=["GET"])
def server_data():
    instance_id = request.args['instance_id']
    server = Server.query.filter_by(instance_id=instance_id).first()

    plugins_list = ""
    for plugin in server.enabled_plugins:
        plugins_list += plugin.file_name + ','

    return jsonify({
            "id": server.id,
            "expiry_date": str(server.expiry_date),
            "op": server.op,
            "enabled_plugins": plugins_list
            })

@application.route("/server/<server_id>/properties", methods=["GET"])
def server_properties(server_id):
    server = Server.query.filter_by(id=server_id).first()
    response = make_response(server.properties.generate_file())
    response.headers["content-type"] = "text/plain"
    response.content_type = "text/plain"
    return response

@application.route("/servers", methods=["GET"])
@login_required
def servers():
    return render_template('servers.html', servers = current_user.servers)

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


        # plugins
        enabled_plugins = request.form.getlist("plugins")

        print(enabled_plugins)

        server.enabled_plugins = []
        for enabled_plugin in enabled_plugins:
            server.enabled_plugins.append(Plugin.query.filter_by(file_name=enabled_plugin).first())


        db.session.commit()

        server.reboot_instance()

        return redirect("/server/"+server_id)


    else:
        plugins = {}
        for plugin in Plugin.query.all():
            plugins[plugin.file_name] = plugin.nice_name

        plugin_descriptions = {}
        for plugin in Plugin.query.all():
            plugin_descriptions[plugin.file_name] = plugin.description

        enabled_plugins = []
        for plugin in server.enabled_plugins:
            enabled_plugins.append(plugin.file_name)

        print(enabled_plugins)

        return render_template('dashboard.html',
                               id = server.id,
                               name = server.properties.server_name,
                               motd = server.properties.motd,
                               mobs = server.properties.spawn_mobs,
                               plugins = plugins,
                               enabled_plugins = enabled_plugins,
                               plugin_descriptions = plugin_descriptions
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

                db.session.add(models.LogEntry('Server '+server.id+' topped up by 30 days'))
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
    db.session.add(models.LogEntry('Server message \"'+command+'\" sent to server '+server.id))

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

