#!/bin/bash

BASE_REGION=eu-west-1
BASE_STACK_NAME=msv

GIT_BRANCH=$(git symbolic-ref --short -q HEAD)

echo "Note: this will spin up a stack for the current Git branch ($GIT_BRANCH)."

: ${MSV_GITHUB_TOKEN?"Need to set MSV_GITHUB_TOKEN. Try running with MSV_GITHUB_TOKEN=xyz123 ./spin-up.sh"}

stack_exists=`aws cloudformation --region $BASE_REGION describe-stacks --stack-name $BASE_STACK_NAME`

if [ -n "$stack_exists" ]; then

    echo "Stack exists. Updating."

    aws cloudformation \
        --region $BASE_REGION \
        update-stack \
        --stack-name $BASE_STACK_NAME-$GIT_BRANCH \
        --template-body file://cloudformation/cloudformation.yaml \
        --parameters ParameterKey=GitBranch,ParameterValue=$GIT_BRANCH \
        ParameterKey=KeyPair,ParameterValue=id_rsa ParameterKey=FlaskDebug,ParameterValue=True ParameterKey=GithubToken,ParameterValue=$MSV_GITHUB_TOKEN ParameterKey=DatabasePassword,ParameterValue=123moon12 ParameterKey=StripePublishableKey,ParameterValue=$MSV_STRIPE_PK ParameterKey=StripeSecretKey,ParameterValue=$MSV_STRIPE_SK ParameterKey=AdminPassword,ParameterValue=$MSV_ADMIN_PASS ParameterKey=Beta,ParameterValue=True --capabilities CAPABILITY_IAM

else

    echo "Launching stack $BASE_STACK_NAME-$GIT_BRANCH"

    aws cloudformation \
        --region $BASE_REGION \
        create-stack \
        --stack-name $BASE_STACK_NAME-$GIT_BRANCH \
        --template-body file://cloudformation/cloudformation.yaml \
        --parameters ParameterKey=GitBranch,ParameterValue=$GIT_BRANCH \
        ParameterKey=KeyPair,ParameterValue=id_rsa ParameterKey=FlaskDebug,ParameterValue=True ParameterKey=GithubToken,ParameterValue=$MSV_GITHUB_TOKEN ParameterKey=DatabasePassword,ParameterValue=123moon12 ParameterKey=StripePublishableKey,ParameterValue=$MSV_STRIPE_PK ParameterKey=StripeSecretKey,ParameterValue=$MSV_STRIPE_SK ParameterKey=AdminPassword,ParameterValue=$MSV_ADMIN_PASS ParameterKey=Beta,ParameterValue=True --capabilities CAPABILITY_IAM
fi

exit 0
