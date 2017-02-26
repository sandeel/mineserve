import os
from datetime import timedelta

APP_NAME = os.getenv('APP_NAME')

# aws settings
AWS_REGION = "eu-west-1"
EC2_KEYPAIR = "id_rsa"
CONTAINER_AGENT_INSTANCE_PROFILE = "mineserve-agent"
CONTAINER_AGENT_AMI = "ami-48f9a52e"
STUB_AWS_RESOURCES = (os.getenv('STUB_AWS_RESOURCES', 'True') == 'True')
POOL_ID = "eu-west-1_HMLKJ8toC"

# app settings
BETA = True
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
ADVSRVS_BETA = "False"
ADVSRVS_ADMIN_PASSWORD = "password"
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True')
ADVSRVS_RESOURCES_ENDPOINT = "s3-us-west-2.amazonaws.com/resources-testing"
ADMIN_PASSWORD = "password"

#jwt
SECRET_KEY = 'super-secret'
JWT_SECRET_KEY = 'super-secret'
JWT_EXPIRATION_DELTA = timedelta(seconds=600)
