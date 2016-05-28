from flask import Flask, request, redirect
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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['AWS_REGION'] = 'us-west-2'
app.config['BETA'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


# stripe setup
stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
  }

stripe.api_key = stripe_keys['secret_key']


app.secret_key = 'super secret'

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class PromoCode(db.Model):
    code = db.Column(db.String, primary_key=True)
    activated = db.Column(db.Boolean)
    reward_code = db.Column(db.String)
    
    def __init__(self, reward_code='BetaTest'):
        self.code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.activated = False
        self.reward_code = reward_code

# Customized promo code admin
class PromoCodeAdmin(sqla.ModelView):
    column_display_pk=True

    form_choices = { 'reward_code': [ ('0', 'BetaTest'),],}

# Customized log admin
class LogAdmin(sqla.ModelView):
    column_default_sort = ('date', True)

class LogEntry(db.Model):
    __tablename__ = 'logentry'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    message = db.Column(db.String)

    def __init__(self, message):
        self.date = datetime.datetime.now()
        self.message = message


class User(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String, primary_key=True)
    hashed_password = db.Column(db.String)

    def __init__(self, email):
        # generate a password to give the user and store the hash
        self.password = str(''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(8)))
        self.hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())
        self.email = email

    def check_password(self, password):
        if bcrypt.hashpw(password, hashed) == self.hashed_password:
            return True
        else:
            return False

# Customized user admin view
class UserAdmin(sqla.ModelView):
    column_display_pk=True

class Properties(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.String, db.ForeignKey('server.id'))
    server = db.relationship("Server", back_populates="_properties")

    #properties
    server_name = db.Column(db.String)
    motd = db.Column(db.String)
    server_port = db.Column(db.String)
    memory_limit= db.Column(db.String)
    gamemode = db.Column(db.String)
    max_players = db.Column(db.String)
    spawn_protection = db.Column(db.String)
    level_name = db.Column(db.String)
    level_type = db.Column(db.String)
    announce_player_achievements = db.Column(db.String)
    white_list = db.Column(db.String)
    enable_query = db.Column(db.String)
    enable_rcon = db.Column(db.String)
    allow_flight = db.Column(db.String)
    spawn_animals = db.Column(db.String)
    spawn_mobs = db.Column(db.String)
    force_gamemode = db.Column(db.String)
    hardcore = db.Column(db.String)
    pvp = db.Column(db.String)
    difficulty = db.Column(db.String)
    generator_settings = db.Column(db.String)
    level_seed = db.Column(db.String)
    rcon_password = db.Column(db.String)
    auto_save = db.Column(db.String)

    def __init__(self,):
        
        # set the default properties
        self.server_name = 'The Server'
        self.motd = 'Adventure Servers Server'
        self.server_port = '19132'
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
        file += 'server-name='+self.server_name+'\n'
        file += 'motd='+self.motd+'\n'
        file += 'server-port='+self.server_port+'\n'
        file += 'memory-limit='+self.memory_limit+'\n'
        file += 'gamemode='+self.gamemode+'\n'
        file += 'max-players='+self.max_players+'\n'
        file += 'spawn-sprotection'+self.spawn_protection+'\n'
        file += 'level-name='+self.level_name+'\n'
        file += 'level-type='+self.level_type+'\n'
        file += 'announce-player-achievements='+self.announce_player_achievements+'\n'
        file += 'white-list='+self.white_list+'\n'
        file +=  'enable-query='+self.enable_query+'\n'
        file += 'enable-rcon='+self.enable_rcon+'\n'
        file += 'allow-flight='+self.allow_flight+'\n'
        file += 'spawn-animals='+ self.spawn_animals+'\n'
        file += 'spawn-mobs='+self.spawn_mobs+'\n'
        file += 'force-gamemode='+self.force_gamemode+'\n'
        file += 'hardcore='+self.hardcore+'\n'
        file += 'pvp='+self.pvp+'\n'
        file += 'difficulty='+self.difficulty+'\n'
        file += 'generator-settings='+self.generator_settings+'\n'
        file += 'level-seed='+self.level_seed+'\n'
        file += 'rcon-password='+self.rcon_password+'\n'
        file += 'auto-save='+self.auto_save+'\n'

        return file

class Server(db.Model):

    __tablename__ = 'server'
    id = db.Column(db.String, primary_key=True)
    instance_id = db.Column(db.String)
    op = db.Column(db.String)
    expiry_date = db.Column(db.DateTime)
    creation_date = db.Column(db.DateTime)
    progenitor_email = db.Column(db.String)
    game = db.Column(db.String)
    server_type = db.Column(db.String)
    size = db.Column(db.String)
    _properties = db.relationship("Properties", back_populates="server")

    def __init__(self, progenitor_email, op, server_name='Adventure Servers', game='mcpe', server_type='genisys', size='micro'):
        self.id = str(uuid.uuid4())

        db.session.add(LogEntry('Creating server with ID '+self.id+' User\'s email address is '+progenitor_email))
        db.session.commit()

        self.progenitor_email = progenitor_email
        self.op = op

        self.creation_date=datetime.datetime.now()

        # give 5 hours and 5 minutes free
        now = datetime.datetime.now()
        now_plus_5_hours = now + datetime.timedelta(minutes=305)
        self.expiry_date = now_plus_5_hours

        # instantiate default properties
        self._properties.append(Properties())
        self.properties.server_name = server_name
        self.properties.motd = server_name

        self.size=size
        self.server_type = server_type
        self.game = game

        self.instance_id = self.start_instance()

    @property
    def properties(self):
        return self._properties[0]

    def __str__(self):
        return self.id

    @property
    def ip_address(self):
        client = boto3.client('ec2', region_name=app.config['AWS_REGION'])
        return client.describe_instances(
            InstanceIds=[
                self.instance_id
            ])['Reservations'][0]['Instances'][0]['PublicIpAddress']

    @property
    def status(self):
        client = boto3.client('ec2', region_name=app.config['AWS_REGION'])
        try:
            instance_status =  client.describe_instance_status(
                InstanceIds=[
                    self.instance_id
                ])['InstanceStatuses'][0].get('InstanceStatus').get('Status')
        except:
            instance_status = 'Unknown'

        return instance_status

    def start_instance(self):

        userdata = """#!/bin/bash

HOME=/home/ubuntu

# install docker
cd $HOME
curl -sSL https://get.docker.com/ | sh

# install git
apt-get install -y git

# pip
apt-get -y install python-pip
pip install awscli

# clone repo
HTTPS_REPO_URL=https://git-codecommit.us-east-1.amazonaws.com/v1/repos/mineserve
git clone https://chromium.googlesource.com/chromium/tools/depot_tools
export PATH=`pwd`/depot_tools:"$PATH"
rm -Rf mineserve
git-retry -v clone https://github.com/sandeel/mineserve.git

docker stop atlas

# get phar
curl https://gitlab.com/itxtech/genisys/builds/1461919/artifacts/file/Genisys_1.1dev-93aea9c.phar -o genisys.phar

#get server properties
INSTANCE_ID=curl http://169.254.169.254/latest/meta-data/instance-id
SERVER_ID="""+self.id+"""

curl http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/server/$SERVER_ID/properties -o server.properties

#op the user
echo """+self.op+""" > /home/ubuntu/ops.txt

# start or run container
docker run -itd --name atlas -p 19132:19132 -p 19132:19132/udp -v /home/ubuntu/ops.txt:/srv/genisys/ops.txt -v /home/ubuntu/genisys.phar:/srv/genisys/genisys.phar -v /home/ubuntu/server.properties:/srv/genisys/server.properties -v /home/ubuntu/mineserve/genisys.yml:/srv/genisys/genisys.yml --restart=unless-stopped itxtech/docker-env-genisys || docker start atlas

# install mcrcon
cd $HOME
rm -r mcrcon
git retry -v clone https://github.com/Tiiffi/mcrcon.git
cd mcrcon
gcc -std=gnu11 -pedantic -Wall -Wextra -O2 -s -o mcrcon mcrcon.c

# set up cron to phone home
pip install requests
pip install boto3
echo "*/1 * * * * ubuntu python /home/ubuntu/mineserve/phone_home.py" >> /etc/crontab

echo "Going down for reboot..."
reboot
        """

        # create the instance
        client = boto3.client('ec2', region_name=app.config['AWS_REGION'])
        response = client.run_instances(
                ImageId='ami-9abea4fb',
                InstanceType='t2.'+self.size,
                MinCount = 1,
                MaxCount = 1,
                UserData = userdata,
                KeyName = 'id_rsa',
                IamInstanceProfile={
                    'Name': 'mineserve-agent'
                    },
                SecurityGroupIds=['sg-cf668aa9'],
                DisableApiTermination=True,
                BlockDeviceMappings=[{
                        'DeviceName': '/dev/sda1',
                        'Ebs': {
                            'VolumeSize': 28,
                            }
                        }]
        )
        instance_id = response['Instances'][0]['InstanceId']

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

# Customized server admin
class ServerAdmin(sqla.ModelView):
    column_display_pk=True
    inline_models = [Properties,]
    
    column_list = (
        'id',
        'instance_id',
        'status',
        'creation_date',
        'expiry_date',
        'size',
        'progenitor_email',
    )


@app.route("/api/v0.1/phone_home", methods=["GET"])
def phone_home():
    instance_id = request.args['instance_id']
    server = Server.query.filter_by(instance_id=instance_id).first()

    db.session.add(LogEntry('Server '+server.id+' phoned home.'))

    td = server.expiry_date - datetime.datetime.now()

    seconds_left = td.seconds
    hours_left = td.seconds // 3600

    server_message = ''

    if server.expiry_date < datetime.datetime.now():

        db.session.add(LogEntry('Server '+server.id+' expired, terminating...'))

        client = boto3.client('ec2', region_name=region)
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

    if server_message:
        db.session.add(LogEntry('Server message \"'+server_message+'\" returned to server '+server.id))
    else:
        db.session.add(LogEntry('No server message returned for server '+server.id))

    db.session.commit()

    return jsonify({
            "server_message": server_message
            })

@app.route("/server_data", methods=["GET"])
def server_data():
    instance_id = request.args['instance_id']
    server = Server.query.filter_by(instance_id=instance_id).first()
    return jsonify({
            "id": server.id,
            "expiry_date": str(server.expiry_date),
            "op": server.op,
            })

@app.route("/", methods=["GET"])
def landing_page():
    return render_template('landing_page.html', beta_test=app.config['BETA'])

@app.route("/server/<server_id>/properties", methods=["GET"])
def server_properties(server_id):
    server = Server.query.filter_by(id=server_id).first()
    response = make_response(server.properties.generate_file())
    response.headers["content-type"] = "text/plain"
    response.content_type = "text/plain"
    return response

@app.route("/server/<server_id>", methods=["GET","POST"])
def server(server_id):
            
    topped_up_message = None
    promo_code_applied=False
    invalid_promo_code=False

    if request.method == 'POST':

        if server_id == 'new':

            # if beta need promo code
            if app.config['BETA']:
                if not request.form['promo-code']:
                        return Response('Need promo code', 401)

            if User.query.filter_by(email=request.form['email']).first():
                return 'That user already has a server'

            db.session.add(LogEntry('Customer has requested a new server'))

            # if server doesn't exist create it
            new_server = Server(progenitor_email=request.form['email'],
                                op=request.form['minecraft_name'],
                                server_name=request.form['server_name'])
            new_server.apply_promo_code(request.form['promo-code'])
            new_server.op=request.form['minecraft_name']
            db.session.add(new_server)
            server_id = new_server.id

            # create the user
            user = User(email=request.form['email'])
            db.session.add(user)

            db.session.commit()
            return redirect('/server/'+server_id)

        elif request.form.get('stripeToken', None):

            server = Server.query.filter_by(id=server_id).first()

            amount = 4000

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

            server.expiry_date = server.expiry_date + datetime.timedelta(days=30)
            db.session.add(server)
            db.session.commit()

            topped_up_message = "Topped up by 30 days."

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
            ip=server.ip_address,
            key=stripe_keys['publishable_key'],
            status=server.status,
            new_server=True,
            topped_up_message=topped_up_message,
            beta=app.config['BETA'],
            invalid_promo_code=invalid_promo_code,
            )

# Create admin
admin = admin.Admin(app, name='Example: SQLAlchemy', template_mode='bootstrap3')
admin.add_view(ServerAdmin(Server,db.session))
admin.add_view(UserAdmin(User,db.session))
admin.add_view(PromoCodeAdmin(PromoCode,db.session))
admin.add_view(LogAdmin(LogEntry,db.session))


if __name__ == '__main__':
    manager.run()


