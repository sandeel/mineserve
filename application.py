from flask import Flask, url_for, redirect, render_template, request, abort
import flask.ext.login as flask_login
from flask_sqlalchemy import SQLAlchemy
import uuid
import boto3
import datetime
from flask import jsonify
from flask import render_template
from flask import request
from flask import redirect
import stripe
import os
import flask_admin as admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import filters
import bcrypt
import random
import string
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import flask.ext.login as flask_login
from flask import Response
from flask import make_response
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user, roles_accepted
from flask_security.utils import encrypt_password
from flask_admin import helpers as admin_helpers
import config
from flask_mail import Mail
import logging
import logging.handlers
import time
from subprocess import Popen
import builtins

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = '/opt/python/log/flask.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())


application = Flask(__name__)
mail = Mail(application)
application.config['MYSQL_DATABASE_USER'] = os.environ['ADVSRVS_MYSQL_DATABASE_USER']
application.config['MYSQL_DATABASE_PASSWORD'] = os.environ['ADVSRVS_MYSQL_DATABASE_PASSWORD']
application.config['MYSQL_DATABASE_DB'] = os.environ['ADVSRVS_MYSQL_DATABASE_DB']
application.config['MYSQL_DATABASE_HOST'] = os.environ['ADVSRVS_MYSQL_DATABASE_HOST']
application.config['AWS_REGION'] = os.environ['ADVSRVS_AWS_REGION']
application.config['BETA'] = (os.environ['ADVSRVS_BETA'] == 'True')
application.config['SG_ID'] = os.environ['ADVSRVS_SG_ID']
application.config['CONTAINER_AGENT_SUBNET'] = os.environ['ADVSRVS_CONTAINER_AGENT_SUBNET']
application.config['CONTAINER_AGENT_INSTANCE_PROFILE'] = os.environ['ADVSRVS_CONTAINER_AGENT_INSTANCE_PROFILE']
application.config['EC2_KEYPAIR'] = os.environ['ADVSRVS_EC2_KEYPAIR']
application.config['ADMIN_PASSWORD'] = os.environ['ADVSRVS_ADMIN_PASSWORD']
application.config['PHONE_HOME_ENDPOINT'] = ('https://'+os.environ['ADVSRVS_PHONE_HOME_ENDPOINT'])
application.config['RESOURCES_ENDPOINT'] = ('https://'+os.environ['ADVSRVS_RESOURCES_ENDPOINT'])
application.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
application.config['SECURITY_PASSWORD_SALT'] = 'mine'
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+application.config['MYSQL_DATABASE_USER']+':'+application.config['MYSQL_DATABASE_PASSWORD']+'@'+application.config['MYSQL_DATABASE_HOST']+'/'+application.config['MYSQL_DATABASE_DB']
application.config['SECURITY_RECOVERABLE'] = True
application.config['SECURITY_CONFIRMABLE'] = False
application.config['SECURITY_REGISTERABLE'] = True
application.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'
application.config['SECURITY_RESET_PASSWORD_TEMPLATE'] = 'reset.html'
application.config['SECURITY_FORGOT_PASSWORD_TEMPLATE'] = 'reset.html'
application.config['SECURITY_CHANGE_PASSWORD_TEMPLATE'] = 'change_password.html'
application.config['SECURITY_CHANGEABLE'] = True
application.config['CONTAINER_AGENT_AMI'] = os.environ['ADVSRVS_CONTAINER_AGENT_AMI']
application.debug = (os.environ['FLASK_DEBUG'] == 'True')

db = SQLAlchemy(application)
migrate = Migrate(application, db)
manager = Manager(application)
manager.add_command('db', MigrateCommand)
login_manager = flask_login.LoginManager()
login_manager.init_app(application)

# stripe setup
stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
  }

stripe.api_key = stripe_keys['secret_key']

application.secret_key = 'super secret'

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    servers = db.relationship('Server', backref=db.backref('user'))

    def __str__(self):
        return self.email

# Create customized model view class
class ProtectedModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(application, user_datastore)

# Executes before the first request is processed.
@application.before_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    db.create_all()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin', description='Administrator')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    encrypted_password = encrypt_password(application.config['ADMIN_PASSWORD'])
    if not user_datastore.get_user('adventureservers@kolabnow.com'):
        user_datastore.create_user(email='adventureservers@kolabnow.com', password=encrypted_password)

    # Commit any database changes; the User and Roles must exist before we can add a Role to the User
    db.session.commit()

    # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    user_datastore.add_role_to_user('adventureservers@kolabnow.com', 'admin')
    db.session.commit()

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )

association_table = db.Table('association', db.Model.metadata,
    db.Column('left_id', db.String(255), db.ForeignKey('server.id')),
    db.Column('right_id', db.Integer, db.ForeignKey('plugin.id'))
)

class Plugin(db.Model):
    __tablename__ = 'plugin'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255))
    nice_name = db.Column(db.String(255))
    description = db.Column(db.String(1024))
    server_id = db.Column(db.String(255), db.ForeignKey('server.id'))
    servers = db.relationship(
        "Server",
        secondary=association_table,
        back_populates="enabled_plugins")
    
    def __init__(self, file_name="", nice_name="Plugin", description=""):
        self.file_name = file_name
        self.nice_name = nice_name
        self.description = description


class PromoCode(db.Model):
    code = db.Column(db.String(255), primary_key=True)
    activated = db.Column(db.Boolean)
    reward_code = db.Column(db.String(255))
    
    def __init__(self, reward_code='BetaTest'):
        self.code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.activated = False
        self.reward_code = reward_code

# Customized promo code admin
class PromoCodeAdmin(ProtectedModelView):
    column_display_pk=True

    form_choices = { 'reward_code': [ ('BetaTest', 'BetaTest'),],}

# Customized log admin
class LogAdmin(ProtectedModelView):
    column_default_sort = ('date', True)

class LogEntry(db.Model):
    __tablename__ = 'logentry'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    message = db.Column(db.String(1024))

    def __init__(self, message):
        self.date = datetime.datetime.now()
        self.message = message

# Customized user admin view
class UserAdmin(ProtectedModelView):
    column_display_pk=True

class Properties(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.String(255), db.ForeignKey('server.id'))

    #properties
    server_name = db.Column(db.String(255))
    motd = db.Column(db.String(255))
    server_port = db.Column(db.String(255))
    memory_limit= db.Column(db.String(255))
    gamemode = db.Column(db.String(255))
    max_players = db.Column(db.String(255))
    spawn_protection = db.Column(db.String(255))
    level_name = db.Column(db.String(255))
    level_type = db.Column(db.String(255))
    announce_player_achievements = db.Column(db.String(255))
    white_list = db.Column(db.String(255))
    enable_query = db.Column(db.String(255))
    enable_rcon = db.Column(db.String(255))
    allow_flight = db.Column(db.String(255))
    spawn_animals = db.Column(db.String(255))
    spawn_mobs = db.Column(db.String(255))
    force_gamemode = db.Column(db.String(255))
    hardcore = db.Column(db.String(255))
    pvp = db.Column(db.String(255))
    difficulty = db.Column(db.String(255))
    generator_settings = db.Column(db.String(255))
    level_seed = db.Column(db.String(255))
    rcon_password = db.Column(db.String(255))
    auto_save = db.Column(db.String(255))

    def __init__(self, server_id):

        self.server_id = server_id
        
        # set the default properties
        self.server_name = 'The Server'
        self.motd = 'Adventure Servers Server'
        self.server_port = '33775'
        self.memory_limit = ''
        self.gamemode = '0'
        self.max_players = '60'
        self.spawn_protection = '16'
        self.level_name = 'world'
        self.level_type = 'DEFAULT'
        self.announce_player_achievements = 'on'
        self.white_list = 'off'
        self.enable_query = 'on'
        self.enable_rcon = 'on'
        self.allow_flight = 'off'
        self.spawn_animals = 'on'
        self.spawn_mobs = 'off'
        self.force_gamemode = 'on'
        self.hardcore = 'off'
        self.pvp = 'on'
        self.difficulty = '1'
        self.generator_settings = ''
        self.level_seed = ''
        self.rcon_password = 'password'
        self.auto_save = 'yes'

    def generate_file(self):

        file = ""
        file += 'server-name='+str(self.server_name)+'\n'
        file += 'motd='+str(self.motd)+'\n'
        file += 'server-port='+str(self.server_port)+'\n'
        file += 'memory-limit='+str(self.memory_limit)+'\n'
        file += 'gamemode='+str(self.gamemode)+'\n'
        file += 'max-players='+str(self.max_players)+'\n'
        file += 'spawn-sprotection='+str(self.spawn_protection)+'\n'
        file += 'level-name='+str(self.level_name)+'\n'
        file += 'level-type='+str(self.level_type)+'\n'
        file += 'announce-player-achievements='+str(self.announce_player_achievements)+'\n'
        file += 'white-list='+str(self.white_list)+'\n'
        file +=  'enable-query='+str(self.enable_query)+'\n'
        file += 'enable-rcon='+str(self.enable_rcon)+'\n'
        file += 'allow-flight='+str(self.allow_flight)+'\n'
        file += 'spawn-animals='+str( self.spawn_animals)+'\n'
        file += 'spawn-mobs='+str(self.spawn_mobs)+'\n'
        file += 'force-gamemode='+str(self.force_gamemode)+'\n'
        file += 'hardcore='+str(self.hardcore)+'\n'
        file += 'pvp='+str(self.pvp)+'\n'
        file += 'difficulty='+str(self.difficulty)+'\n'
        file += 'generator-settings='+str(self.generator_settings)+'\n'
        file += 'level-seed='+str(self.level_seed)+'\n'
        file += 'rcon.password='+str(self.rcon_password)+'\n'
        file += 'auto-save='+str(self.auto_save)+'\n'

        return file

class Server(db.Model):

    __tablename__ = 'server'
    id = db.Column(db.String(255), primary_key=True)
    instance_id = db.Column(db.String(255))
    op = db.Column(db.String(255))
    expiry_date = db.Column(db.DateTime)
    creation_date = db.Column(db.DateTime)
    owner = db.Column(db.String(255))
    game = db.Column(db.String(255))
    server_type = db.Column(db.String(255))
    size = db.Column(db.String(255))
    properties = db.relationship("Properties", backref="server", uselist=False)
    enabled_plugins = db.relationship("Plugin",
                    secondary=association_table,
                    back_populates="servers")
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship("User", back_populates="servers")

    sizes = ['micro']

    prices = {
                'micro': 1000
                }

    max_players = {
                    'micro': 20
                    }

    def __init__(self, op, server_name='Adventure Servers', game='mcpe', server_type='genisys', size='micro'):
        self.id = str(uuid.uuid4())

        db.session.add(LogEntry('Creating server with ID '+self.id))
        db.session.commit()

        self.op = op

        self.creation_date=datetime.datetime.now()

        # give 1 hour and 5 minutes free
        now = datetime.datetime.now()
        now_plus_1_hours = now + datetime.timedelta(minutes=65)
        self.expiry_date = now_plus_1_hours

        # instantiate default properties
        self.properties = Properties(server_id = self.id)
        self.properties.server_name = server_name

        # random seed
        random.seed(server_name)
        self.properties.level_seed = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(32))

        self.properties.motd = server_name

        self.size=size
        self.server_type = server_type
        self.game = game

        self.instance_id = self.start_instance()

        db.session.add(self)
        db.session.commit()

    def __str__(self):
        return self.id

    @property
    def status(self):
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        try:
            instance_status =  client.describe_instance_status(
                InstanceIds=[
                    self.instance_id
                ])['InstanceStatuses'][0].get('InstanceStatus').get('Status')
        except:
            instance_status = 'Unknown'

        if instance_status == 'ok' and ((datetime.datetime.now() - self.creation_date).seconds < 120):
            instance_status = 'Preparing Genisys'

        return instance_status

    @property
    def ip(self):
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        try:
            instance_status =  client.describe_instances(
                InstanceIds=[
                    self.instance_id
                ])['Reservations'][0]['Instances'][0]['PublicIpAddress']
        except:
            instance_status = 'Unknown'

        return instance_status

    @property
    def private_ip(self):
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        try:
            private_ip =  client.describe_instances(
                InstanceIds=[
                    self.instance_id
                ])['Reservations'][0]['Instances'][0]['PrivateIpAddress']
        except:
            private_ip = 'Unknown'

        return private_ip

    def start_instance(self):
        phone_home_endpoint = '\\"'+application.config['PHONE_HOME_ENDPOINT']+'\\"'
        resources_endpoint = '\\"'+application.config['RESOURCES_ENDPOINT']+'\\"'

        userdata = """#!/bin/bash
cd /home/ubuntu
echo { \\"phone_home_endpoint\\": """+phone_home_endpoint+""", \\"resources_endpoint\\": """+resources_endpoint+""" } > /home/ubuntu/config.json
curl -sSL https://get.docker.com/ | sh
echo "cd /home/ubuntu && rm -rf bootstrap_instance.sh && wget --no-check-certificate https://raw.githubusercontent.com/sandeel/mineserve/master/bootstrap_instance.sh && /bin/bash /home/ubuntu/bootstrap_instance.sh" > /etc/rc.local
echo "exit 0" >> /etc/rc.local
echo "*/30 * * * * root python /home/ubuntu/phone_home.py" >> /etc/crontab
echo "post-up /sbin/ifconfig eth0 mtu 1454" >> /etc/network/interfaces.d/eth0.cfg
reboot
        """

        # create the instance
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        response = client.run_instances(
                ImageId=application.config['CONTAINER_AGENT_AMI'],
                InstanceType='t2.'+self.size,
                MinCount = 1,
                MaxCount = 1,
                UserData = userdata,
                KeyName = application.config['EC2_KEYPAIR'],
                IamInstanceProfile={
                    'Name': application.config['CONTAINER_AGENT_INSTANCE_PROFILE']
                    },
                SecurityGroupIds=[application.config['SG_ID']],
                BlockDeviceMappings=[{
                        'DeviceName': '/dev/sda1',
                        'Ebs': {
                            'VolumeSize': 28,
                            }
                        }],
                SubnetId=application.config['CONTAINER_AGENT_SUBNET']
        )
        instance_id = response['Instances'][0]['InstanceId']

        time.sleep(1)

        # tag the instance
        response = client.create_tags(
            Resources=[
                instance_id,
            ],
            Tags=[
                {
                    'Key': 'mineserv_role',
                    'Value': 'container_agent'
                },
            ]
        )

        return instance_id

    def apply_promo_code(self,promo_code):
        promo_code = PromoCode.query.filter_by(code=promo_code).first()

        if promo_code and not promo_code.activated:
            self.expiry_date = self.expiry_date + datetime.timedelta(days=30)
            db.session.add(self)

            promo_code.activated=True
            db.session.add(promo_code)

            db.session.add(LogEntry('Promo Code '+promo_code.code+' applied to server '+self.id))

            db.session.commit()

    def reboot_instance(self):
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        response = client.reboot_instances(
            InstanceIds=[
                self.instance_id,
            ]
        )
        return response


# Customized server admin
class ServerAdmin(ProtectedModelView):
    column_display_pk=True
    inline_models = [Plugin,]
    
    column_list = (
        'id',
        'instance_id',
        'status',
        'ip',
        'creation_date',
        'expiry_date',
        'size',
        'progenitor_email',
    )


@application.route("/api/v0.1/phone_home", methods=["GET"])
def phone_home():
    instance_id = request.args['instance_id']
    server = Server.query.filter_by(instance_id=instance_id).first()

    db.session.add(LogEntry('Server '+server.id+' phoned home.'))

    td = server.expiry_date - datetime.datetime.now()

    seconds_left = td.total_seconds()
    hours_left = seconds_left // 3600

    server_message = ''

    if server.expiry_date < datetime.datetime.now():

        db.session.add(LogEntry('Server '+server.id+' expired, terminating...'))

        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        response = client.terminate_instances(
            InstanceIds=[
                instance_id,
            ]
    )
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
        db.session.add(LogEntry('No server message sent for server '+server.id))

    db.session.commit()

    return jsonify({
            "status": "ok"
            })

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


            db.session.add(LogEntry('Customer has requested a new server'))

            if user_datastore.get_user(request.form['email']):
                return render_template('landing_page.html', form_error="That email address has already been taken.")
            else:
                # create the user
                # password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
                encrypted_password = encrypt_password(request.form['password'])

                user_datastore.create_user(email=request.form['email'], password=encrypted_password)

                db.session.commit()

                user = user_datastore.get_user(request.form['email'])
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
        server.properties.server_name = request.form['name']
        server.properties.motd = request.form['motd']

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
                
                db.session.add(LogEntry('Server '+server.id+' topped up by 30 days'))
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
            price=Server.prices[server.size]/100,
            error_message=error_message,
            )

def rcon(server, command):
    Popen(['/opt/mcrcon/mcrcon/mcrcon', '-H', server.private_ip, '-P', '33775', '-p', 'password', command])
    db.session.add(LogEntry('Server message \"'+command+'\" sent to server '+server.id))

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

# Create admin
admin = admin.Admin(application, name='MineServe Admin', template_mode='bootstrap3')
admin.add_view(ServerAdmin(Server,db.session))
admin.add_view(UserAdmin(User,db.session))
admin.add_view(PromoCodeAdmin(PromoCode,db.session))
admin.add_view(LogAdmin(LogEntry,db.session))
admin.add_view(ProtectedModelView(Properties,db.session))
admin.add_view(ProtectedModelView(Plugin,db.session))

@application.template_global(name='zip')
def _zip(*args, **kwargs): #to not overwrite builtin zip in globals
    return builtins.zip(*args, **kwargs)

if __name__ == '__main__':
    manager.run()
