import os
from datetime import timedelta

APP_NAME = os.getenv('APP_NAME',default='msv-testing')

# aws settings
AWS_REGION = "eu-west-1"
EC2_KEYPAIR = "id_rsa"
CONTAINER_AGENT_INSTANCE_PROFILE = "mineserve-agent"




# AMIs for container agents
CONTAINER_AGENT_AMI = {}
CONTAINER_AGENT_AMI['eu-west-1'] = "ami-95f8d2f3" # ireland
CONTAINER_AGENT_AMI['us-east-1'] = "ami-b2df2ca4" # n. virginia
CONTAINER_AGENT_AMI['us-east-2'] = "ami-62745007" # ohio
CONTAINER_AGENT_AMI['us-west-2'] = "ami-62d35c02" # oregon
CONTAINER_AGENT_AMI['ap-southeast-2'] = "ami-fbe9eb98" # sydney




STUB_AWS_RESOURCES = (os.getenv('STUB_AWS_RESOURCES', 'True') == 'True')

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


# auth0
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
