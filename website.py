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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['aws_region'] = 'us-west-2'
app.config['BETA'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


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
    
    def __init__(self, reward_code):
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

class Server(db.Model):

    __tablename__ = 'server'
    id = db.Column(db.String, primary_key=True)
    instance_id = db.Column(db.String)
    hashed_server_key = db.Column(db.String)
    op = db.Column(db.String)
    expiry_date = db.Column(db.DateTime)
    creation_date = db.Column(db.DateTime)
    progenitor_email = db.Column(db.String)

    def __init__(self, progenitor_email, op):
        self.id = str(uuid.uuid4())

        db.session.add(LogEntry('Creating server with ID '+self.id+' User\'s email address is '+progenitor_email))
        db.session.commit()

        self.progenitor_email = progenitor_email
        self.op = op

        self.instance_id = self.start_instance()

        self.creation_date=datetime.datetime.now()

        # give 5 hours and 1 minute free
        now = datetime.datetime.now()
        now_plus_5_hours = now + datetime.timedelta(minutes=301)
        self.expiry_date = now_plus_5_hours

        # generate a random key to give the customer and store the hash
        self.server_key = str(uuid.uuid4())
        self.hashed_server_key = bcrypt.hashpw(self.server_key, bcrypt.gensalt())

    def __str__(self):
        return self.id

    def check_server_key(self, server_key):
        if bcrypt.hashpw(server_key, hashed) == self.hashed_server_key:
            return True
        else:
            return False

    @property
    def ip_address(self):
        client = boto3.client('ec2', region_name=app.config['aws_region'])
        return client.describe_instances(
            InstanceIds=[
                self.instance_id
            ])['Reservations'][0]['Instances'][0]['PublicIpAddress']

    @property
    def status(self):
        client = boto3.client('ec2', region_name=app.config['aws_region'])
        instance_status =  client.describe_instance_status(
            InstanceIds=[
                self.instance_id
            ])['InstanceStatuses']
        if instance_status:
            return instance_status[0].get('InstanceStatus').get('Status')
        else:
            return 'Spinning up'

    def start_instance(self):
        # create the instance
        bootstrap_file = f = open('bootstrap_instance.sh', 'r')
        user_data = bootstrap_file.read()
        client = boto3.client('ec2', region_name='us-west-2')
        response = client.run_instances(
                ImageId='ami-9abea4fb',
                InstanceType='t2.micro',
                MinCount = 1,
                MaxCount = 1,
                UserData = user_data,
                KeyName = 'id_rsa',
                IamInstanceProfile={
                    'Name': 'mineserve-agent'
                    },
                SecurityGroupIds=['sg-cf668aa9'],
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

@app.route("/api/v0.1/phone_home", methods=["GET"])
def phone_home():
    instance_id = request.args['instance_id']
    server = Server.query.filter_by(instance_id=instance_id).first()

    td = server.expiry_date - datetime.datetime.now()

    seconds_left = td.seconds
    hours_left = td.seconds // 3600

    server_message = ''

    if server.expiry_date < datetime.datetime.now():
        db.session.add(LogEntry('Server '+server.id+' expired, terminating...'))
        db.session.commit()
        client = boto3.client('ec2', region_name=region)
        response = client.terminate_instances(
            InstanceIds=[
                instance_id,
            ]
    )
    elif hours_left < 1:
        server_message = "WARNING. Server will be terminated in less than an hour unless topped-up. All data will be lost."
    elif hours_left < 5:
        server_message ="WARNING. 5 hours credit remaining on this server."

    return jsonify({
            "server_message": server_message
            })

@app.route("/server_data", methods=["GET"])
def server_data():
    instance_id = request.args['instance_id']
    server = Server.query.filter_by(instance_id=instance_id).first()
    return jsonify({
            "expiry_date": str(server.expiry_date),
            "op": server.op,
            })

@app.route("/", methods=["GET"])
def landing_page():
    return render_template('landing_page.html')

@app.route("/server/<server_id>", methods=["GET","POST"])
def server(server_id):
            
    topped_up_message = None
    new_server_key= None
    promo_code_applied=False

    if request.method == 'POST':

        db.session.add(LogEntry('Customer has requested a new server'))
        db.session.commit()

        if server_id == 'new':
            # if server doesn't exist create it
            new_server = Server(progenitor_email=request.form['email'],
                                op=request.form['minecraft_name'])
            db.session.add(new_server)
            db.session.commit()
            new_server_key= new_server.server_key
            server_id = new_server.id
            return redirect('/server/'+server_id)

        elif request.form.get('stripeToken', None):

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
            promo_code = PromoCode.query.filter_by(code=request.form['promo-code']).first()

            if promo_code and not promo_code.activated:
                server.expiry_date = server.expiry_date + datetime.timedelta(days=30)
                db.session.add(server)

                promo_code_applied=True
                promo_code.activated=True
                db.session.add(promo_code)

                db.session.add(LogEntry('Promo Code '+promo_code.code+' applied to server '+server.id))

                db.session.commit()

    server = Server.query.filter_by(id=server_id).first()

    if (datetime.datetime.now() - server.creation_date).seconds < 3600:
        new_server = True
    else:
        new_server = False

    td = server.expiry_date - datetime.datetime.now()
    days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

    if not request.args:
        server_key = None
    else:
        server_key = request.args['server_key']

    return render_template('server.html',
            time_remaining=str(days)+' days, '+str(hours)+' hours, '+str(minutes)+' minutes',
            id=server.id,
            ip=server.ip_address,
            key=stripe_keys['publishable_key'],
            status=server.status,
            new_server=True,
            topped_up_message=topped_up_message,
            server_key=server_key,
            beta=app.config['BETA'],
            )

# Create admin
admin = admin.Admin(app, name='Example: SQLAlchemy', template_mode='bootstrap3')
admin.add_view(sqla.ModelView(Server,db.session))
admin.add_view(PromoCodeAdmin(PromoCode,db.session))
admin.add_view(LogAdmin(LogEntry,db.session))


if __name__ == '__main__':
    manager.run()
