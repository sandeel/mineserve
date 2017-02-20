#!/bin/bash

BASE_REGION=eu-west-1
BASE_STACK_NAME=msv

stack_exists=`aws cloudformation --region $BASE_REGION describe-stacks --stack-name $BASE_STACK_NAME`

if [ -n "$stack_exists" ]; then
    aws cloudformation --region $BASE_REGION update-stack --stack-name $BASE_STACK_NAME --template-body file://cloudformation/cloudformation.yaml --parameters ParameterKey=KeyPair,ParameterValue=id_rsa ParameterKey=FlaskDebug,ParameterValue=True ParameterKey=GithubToken,ParameterValue=$MSV_GITHUB_TOKEN ParameterKey=DatabasePassword,ParameterValue=123moon12 ParameterKey=StripePublishableKey,ParameterValue=$MSV_STRIPE_PK ParameterKey=StripeSecretKey,ParameterValue=$MSV_STRIPE_SK ParameterKey=AdminPassword,ParameterValue=$MSV_ADMIN_PASS ParameterKey=Beta,ParameterValue=True --capabilities CAPABILITY_IAM
else
    aws cloudformation --region $BASE_REGION create-stack --stack-name $BASE_STACK_NAME --template-body file://cloudformation/cloudformation.yaml --parameters ParameterKey=KeyPair,ParameterValue=id_rsa ParameterKey=FlaskDebug,ParameterValue=True ParameterKey=GithubToken,ParameterValue=$MSV_GITHUB_TOKEN ParameterKey=DatabasePassword,ParameterValue=123moon12 ParameterKey=StripePublishableKey,ParameterValue=$MSV_STRIPE_PK ParameterKey=StripeSecretKey,ParameterValue=$MSV_STRIPE_SK ParameterKey=AdminPassword,ParameterValue=$MSV_ADMIN_PASS ParameterKey=Beta,ParameterValue=True --capabilities CAPABILITY_IAM
fi
