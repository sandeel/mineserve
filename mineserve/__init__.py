from flask import Flask, url_for, render_template, request, abort
import flask.ext.login as flask_login
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import stripe
import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask import make_response
from flask_mail import Mail
from subprocess import Popen
import builtins
from flask_security import SQLAlchemyUserDatastore
import datetime
import yaml

with open('config.yaml', 'r') as f:
        config = yaml.load(f)

application = Flask(__name__)
mail = Mail(application)
application.config['MYSQL_DATABASE_USER'] = os.environ['ADVSRVS_MYSQL_DATABASE_USER']
application.config['MYSQL_DATABASE_PASSWORD'] = os.environ['ADVSRVS_MYSQL_DATABASE_PASSWORD']
application.config['MYSQL_DATABASE_DB'] = os.environ['ADVSRVS_MYSQL_DATABASE_DB']
application.config['MYSQL_DATABASE_HOST'] = os.environ['ADVSRVS_MYSQL_DATABASE_HOST']
application.config['AWS_REGION'] = os.environ['ADVSRVS_AWS_REGION']
application.config['BETA'] = (os.environ['ADVSRVS_BETA'] == 'True')
application.config['SG_ID'] = config['aws']['security_group_id']
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
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['TASK_DEFINITION'] = os.environ['TASK_DEFINITION']
application.debug = (os.environ['FLASK_DEBUG'] == 'True')

db = SQLAlchemy(application)
migrate = Migrate(application, db)
manager = Manager(application)
manager.add_command('db', MigrateCommand)
login_manager = flask_login.LoginManager()
login_manager.init_app(application)

application.secret_key = 'super secret'

# stripe setup
stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
  }

stripe.api_key = stripe_keys['secret_key']

@application.template_global(name='zip')
def _zip(*args, **kwargs): #to not overwrite builtin zip in globals
    return builtins.zip(*args, **kwargs)

import mineserve.views
