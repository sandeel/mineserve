## How to install and run locally

### Install a local DynamoDB

When running locally you can use a local version of DynamoDB. Set STUB_AWS_RESOURCES setting on the environment to create 'fake' servers in the local databse.

Follow the steps here to download and run DynamoDB locally on port 8000: http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html

Create a table for servers on the local DynamoDB table:

    aws dynamodb create-table --table-name msv-testing-servers --attribute-definitions AttributeName=id,AttributeType=S AttributeName=user,AttributeType=S --endpoint-url http://localhost:8000 --region eu-west-1 --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 --global-secondary-indexes IndexName=user-index,KeySchema="{AttributeName='user',KeyType=HASH}",Projection={ProjectionType=ALL},ProvisionedThroughput="{ReadCapacityUnits=1,WriteCapacityUnits=1}"


### Setting up the local Flask app

Recommended to use Python 3.

(Optional but recommended) Use a virtualenv:

    mkvirtualenv mineserve

### Clone the environment

    git clone git@github.com:sandeel/mineserve.git && cd mineserve

### Install the requirements

    pip install -R requirements.txt

### Run the API server

Run the API server locally (eg. on port 8080) with debug on and STUB_AWS_RESOURCES on. The local copy of the app will then automatically the local DynamDB running on port 8000.

    FLASK_DEBUG=True STUB_AWS_RESOURCES=True python application.py runserver -h 0.0.0.0 -p 8080


### Examples of use:

Get my servers:

    curl localhost:8080/api/0.1/servers -H 'Authorization: Bearer my_jwt_token'

Create a new server:

    curl localhost:8080/api/0.1/servers  -X POST -H 'Authorization: Bearer my_jwt_token' -d '{ "name": "Jurassic Ark", "type": "ark_server", "size": "large", "region": "us-east-1" }'

Top up a server by 30 days:

    Use generate_stripe_token.py to get a Stripe token.

    curl -H "Authorization: Bearer my_jwt_token" localhost:8000/api/0.1/servers/the_server_id/topup -X POST -d '{"stripeToken": "tok_19xNbgFS8gnfcxztAca3WWe8"}'

## Running on AWS

The manage.sh script in the root directory should be able to automatically spin up the needed infrastructure on AWS. You'll need to have the AWS CLI tool [1] installed and have authentication set up, as the script will make use of AWS CLI calls.

### Usage:

To spin up the resources:

    ./manage.sh spin-up

Note you'll need to authenticate the script to Github with Oauth token in environment variables MSV_GITHUB_TOKEN. This can be done as a one-liner like

    GITHUB_TOKEN=12345 ./manage.sh spin-up

To terminate all the resources:

    ./manage.sh spin-down

[1] AWS CLI https://aws.amazon.com/cli/tool 
