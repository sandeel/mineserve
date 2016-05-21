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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    expiry_date = db.Column(db.DateTime)

    def __init__(self, user):
        self.id = str(uuid.uuid4())
        self.user_id = user.id

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
                    }
        )
        self.instance_id = response['Instances'][0]['InstanceId']

        # tag the instance
        response = client.create_tags(
            Resources=[
                self.instance_id,
            ],
            Tags=[
                {
                    'Key': 'mineserv_role',
                    'Value': 'container_agent'
                },
                {
                    'Key': 'user_id',
                    'Value': self.user_id
                },
            ]
        )

        now = datetime.datetime.now()
        now_plus_10 = now + datetime.timedelta(minutes = 10)
        self.expiry_date = now_plus_10


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)
    servers = db.relationship("Server", backref="user")

    def __init__(self, email, password):
        self.id = str(uuid.uuid4())
        self.email = email
        self.password = bcrypt.hashpw(password.encode('UTF_8'), bcrypt.gensalt())

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object."""
    return User.query.get(user_id)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='pw' id='pw' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form>
               '''

    email = request.form['email']
    user = User.query.get(email)
    if user:
        if bcrypt.hashpw(request.form['pw'].encode('UTF_8'), user.password) == user.password:
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            flask_login.login_user(user, remember=True)
            return redirect("/server")

    return 'Bad login'

@app.route("/logout", methods=["GET"])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return 'Logged out'

@app.route("/server", methods=["GET"])
@flask_login.login_required
def server():
    return 'the server'

@app.route("/get_expiry_of_instance", methods=["POST"])
def get_expiry_of_instance():
    content = request.json
    instance_id = content['instance_id']
    server = Server.query.filter_by(instance_id=instance_id).first()
    return str(server.expiry_date)

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
