from flask import Flask, request, redirect
import flask.ext.login as flask_login
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import uuid
import boto3
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

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

        now = datetime.datetime.now()
        now_plus_10 = now + datetime.timedelta(minutes = 10)
        self.expiry_date = now_plus_10

    def start_instance(self):
        # create the instance
        bootstrap_file = f = open('bootstrap_instance.sh', 'r')
        user_data = bootstrap_file.read()
        client = boto3.client('ec2', region_name='us-west-2')
        response = client.run_instances(
                ImageId='ami-9abea4fb',
                InstanceType='m4.large',
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

@app.route("/get_server_data_for_instance", methods=["POST"])
def get_expiry_of_instance():
    content = request.json
    instance_id = content['instance_id']
    server = Server.query.filter_by(instance_id=instance_id).first()
    return {
            "expiry_date": server.expiry_date,
            "op": server.op,
            }

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
