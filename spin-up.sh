#!/bin/bash

aws cloudformation --region eu-west-1 create-stack --stack-name msv --template-body file://cloudformation/cloudformation.yaml --parameters ParameterKey=KeyPair,ParameterValue=id_rsa ParameterKey=FlaskDebug,ParameterValue=True ParameterKey=GithubToken,ParameterValue=$MSV_GITHUB_TOKEN ParameterKey=DatabasePassword,ParameterValue=123moon12 ParameterKey=StripePublishableKey,ParameterValue=$MSV_STRIPE_PK ParameterKey=StripeSecretKey,ParameterValue=$MSV_STRIPE_SK ParameterKey=AdminPassword,ParameterValue=$MSV_ADMIN_PASS ParameterKey=Beta,ParameterValue=True --capabilities CAPABILITY_IAM
