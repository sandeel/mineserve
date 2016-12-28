import os
from datetime import timedelta

# aws settings
AWS_REGION = "eu-west-1"
EC2_KEYPAIR = "id_rsa"
CONTAINER_AGENT_INSTANCE_PROFILE = "mineserve-agent"
CONTAINER_AGENT_AMI = "ami-a1491ad2"
STUB_AWS_RESOURCES = (os.getenv('STUB_AWS_RESOURCES', 'True') == 'True')
POOL_ID = "eu-west-1_HMLKJ8toC"

# database settings
MYSQL_DATABASE_USER = os.getenv('DB_USER', 'root')
MYSQL_DATABASE_PASSWORD = os.getenv('DB_PASS','')
MYSQL_DATABASE_DB = os.getenv('DB_NAME', 'mineserve')
MYSQL_DATABASE_HOST = os.getenv('DB_HOST','localhost')

# app settings
BETA = True
STRIPE_SECRET_KEY = "sk_test_T86oR2vE8opYYtbfbYRV6Oz9"
STRIPE_PUBLISHABLE_KEY = "pk_test_2d9cGno2Xf42e9zZZ9Oh3y1V"
ADVSRVS_BETA = "False"
ADVSRVS_ADMIN_PASSWORD = "password"
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True')
ADVSRVS_RESOURCES_ENDPOINT = "s3-us-west-2.amazonaws.com/resources-testing"
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'mine'
SQLALCHEMY_DATABASE_URI = 'mysql://'+MYSQL_DATABASE_USER+':'+MYSQL_DATABASE_PASSWORD+'@'+MYSQL_DATABASE_HOST+'/'+MYSQL_DATABASE_DB
SECURITY_RECOVERABLE = True
SECURITY_CONFIRMABLE = False
SECURITY_REGISTERABLE = True
SECURITY_LOGIN_USER_TEMPLATE = 'login.html'
SECURITY_RESET_PASSWORD_TEMPLATE = 'reset.html'
SECURITY_FORGOT_PASSWORD_TEMPLATE = 'reset.html'
SECURITY_CHANGE_PASSWORD_TEMPLATE = 'change_password.html'
SECURITY_CHANGEABLE = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
ADMIN_PASSWORD = "password"

#jwt
SECRET_KEY = 'super-secret'
JWT_SECRET_KEY = 'super-secret'
JWT_EXPIRATION_DELTA = timedelta(seconds=600)
