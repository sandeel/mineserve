from flask import Flask, request, redirect
import flask.ext.login as flask_login
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import uuid
import boto3
import datetime
from flask import jsonify
from flask import render_template
from flask import request
from flask import redirect
import stripe
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['aws_region'] = 'us-west-2'
db = SQLAlchemy(app)


# stripe setup
stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
  }

stripe.api_key = stripe_keys['secret_key']


app.secret_key = 'super secret'

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class Server(db.Model):

    __tablename__ = 'server'
    id = db.Column(db.String, primary_key=True)
    instance_id = db.Column(db.String)
    op = db.Column(db.String)
    expiry_date = db.Column(db.DateTime)

    def __init__(self, op):
        self.id = str(uuid.uuid4())
        self.op = op

        self.instance_id = self.start_instance()

        # give 5 hours and 1 minute free
        now = datetime.datetime.now()
        now_plus_5_hours = now + datetime.timedelta(minutes=301)
        self.expiry_date = now_plus_5_hours

    @property
    def ip_address(self):
        client = boto3.client('ec2', region_name=app.config['aws_region'])
        return client.describe_instances(
            InstanceIds=[
                self.instance_id
            ])['Reservations'][0]['Instances'][0]['PublicIpAddress']

    def start_instance(self):
        # create the instance
        bootstrap_file = f = open('bootstrap_instance.sh', 'r')
        user_data = bootstrap_file.read()
        client = boto3.client('ec2', region_name='us-west-2')
        response = client.run_instances(
                ImageId='ami-9abea4fb',
                InstanceType='t2.small',
                MinCount = 1,
                MaxCount = 1,
                UserData = user_data,
                KeyName = 'id_rsa',
                IamInstanceProfile={
                    'Name': 'mineserve-agent'
                    }
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

@app.route("/server_data", methods=["GET"])
def server_data():
    instance_id = request.args['instance_id']
    server = Server.query.filter_by(instance_id=instance_id).first()
    return jsonify({
            "expiry_date": server.expiry_date),
            "op": server.op,
            })

@app.route("/", methods=["GET"])
def landing_page():
    return render_template('landing_page.html')

@app.route("/create-server", methods=["GET","POST"])
def create_server():
    if request.method == "POST":
        new_server = Server(op=request.form['minecraft_name'])
        db.session.add(new_server)
        db.session.commit()
        return redirect("/server/"+new_server.id)
    return render_template('create_server.html')

@app.route("/server/<server_id>", methods=["GET","POST"])
def server(server_id):
    if request.method == 'GET':
        server = Server.query.filter_by(id=server_id).first()
        td = server.expiry_date - datetime.datetime.now()
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60
        return render_template('server.html',
                time_remaining=str(days)+' days, '+str(hours)+' hours, '+str(minutes)+' minutes',
                id=server.id,
                ip=server.ip_address,
                key=stripe_keys['publishable_key'],
                )

    amount = 4000

    customer = stripe.Customer.create(
        card=request.form['stripeToken'],
        metadata={ "server_id": server_id }
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

    return render_template('server.html', topped_up_message="Top-up successful. 30 days added.")

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)






