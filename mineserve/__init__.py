from flask import Flask
import flask_login
import stripe
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail
import builtins
from flask_cors import CORS

application = Flask(__name__)
mail = Mail(application)
CORS(application)

application.config.from_object('mineserve.default_settings')

application.debug = (application.config['FLASK_DEBUG'] == 'True')

manager = Manager(application)
manager.add_command('db', MigrateCommand)
login_manager = flask_login.LoginManager()
login_manager.init_app(application)

application.secret_key = 'super secret'

# stripe setup
stripe_keys = {
  'secret_key': application.config['STRIPE_SECRET_KEY'],
  'publishable_key': application.config['STRIPE_PUBLISHABLE_KEY']
  }

stripe.api_key = stripe_keys['secret_key']

@application.template_global(name='zip')
def _zip(*args, **kwargs): #to not overwrite builtin zip in globals
    return builtins.zip(*args, **kwargs)

import mineserve.views
