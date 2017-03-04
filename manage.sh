#!/bin/bash

BASE_REGION=eu-west-1
BASE_STACK_NAME=msv
GIT_BRANCH=$(git symbolic-ref --short -q HEAD)
STACK_NAME=$BASE_STACK_NAME-$GIT_BRANCH

key="$1"

case $key in
        spin-up)

        echo "Note: this will spin up a stack for the current Git branch ($GIT_BRANCH)."

        : ${MSV_GITHUB_TOKEN?"Need to set MSV_GITHUB_TOKEN. Try running with MSV_GITHUB_TOKEN=xyz123 ./spin-up.sh"}

        echo "Creating bucket for CloudFormation templates..."
        aws s3 mb s3://msv-templates

        echo "Uploading ark template..."
        aws s3 cp modules/ark/cloudformation/cloudformation.yaml s3://msv-templates/ark.yaml

        stack_exists=`aws cloudformation --region $BASE_REGION describe-stacks --stack-name $STACK_NAME` 2>/dev/null || echo "Stack not found".

        if [ -n "$stack_exists" ]; then

            echo "Stack exists. Updating."

            aws cloudformation \
                --region $BASE_REGION \
                update-stack \
                --stack-name $STACK_NAME \
                --template-body file://cloudformation/cloudformation.yaml \
                --parameters ParameterKey=GitBranch,ParameterValue=$GIT_BRANCH \
                ParameterKey=KeyPair,ParameterValue=id_rsa ParameterKey=FlaskDebug,ParameterValue=True ParameterKey=GithubToken,ParameterValue=$MSV_GITHUB_TOKEN ParameterKey=DatabasePassword,ParameterValue=123moon12 ParameterKey=StripePublishableKey,ParameterValue=$MSV_STRIPE_PK ParameterKey=StripeSecretKey,ParameterValue=$MSV_STRIPE_SK ParameterKey=AdminPassword,ParameterValue=$MSV_ADMIN_PASS ParameterKey=Beta,ParameterValue=True --capabilities CAPABILITY_IAM

        else

            echo "Launching stack $STACK_NAME."

            aws cloudformation \
                --region $BASE_REGION \
                create-stack \
                --stack-name $STACK_NAME \
                --template-body file://cloudformation/cloudformation.yaml \
                --parameters ParameterKey=GitBranch,ParameterValue=$GIT_BRANCH \
                ParameterKey=KeyPair,ParameterValue=id_rsa ParameterKey=FlaskDebug,ParameterValue=True ParameterKey=GithubToken,ParameterValue=$MSV_GITHUB_TOKEN ParameterKey=DatabasePassword,ParameterValue=123moon12 ParameterKey=StripePublishableKey,ParameterValue=$MSV_STRIPE_PK ParameterKey=StripeSecretKey,ParameterValue=$MSV_STRIPE_SK ParameterKey=AdminPassword,ParameterValue=$MSV_ADMIN_PASS ParameterKey=Beta,ParameterValue=True --capabilities CAPABILITY_IAM
        fi

        # eu-west-1 regional
        stack_exists=`aws cloudformation --region eu-west-1 describe-stacks --stack-name $STACK_NAME-regional` 2>/dev/null || echo "Stack not found".
        if [ -n "$stack_exists" ]; then
            echo "Regional stack in eu-west-1 exists. Updating..."
            aws cloudformation update-stack --region eu-west-1 --stack-name $STACK_NAME-regional --template-body file://cloudformation/regional_infrastructure.yaml --parameters ParameterKey=KeyName,ParameterValue='id_rsa'
        else
            echo "Spinning up regional stack for eu-west-1"
            aws cloudformation create-stack --region eu-west-1 --stack-name $STACK_NAME-regional --template-body file://cloudformation/regional_infrastructure.yaml --parameters ParameterKey=KeyName,ParameterValue='id_rsa'
        fi

        # us-east-1 regional
        stack_exists=`aws cloudformation --region us-east-1 describe-stacks --stack-name $STACK_NAME-regional` 2>/dev/null || echo "Stack not found".
        if [ -n "$stack_exists" ]; then
            echo "Regional stack in us-east-1 exists. Updating..."
            aws cloudformation update-stack --region us-east-1 --stack-name $STACK_NAME-regional --template-body file://cloudformation/regional_infrastructure.yaml --parameters ParameterKey=KeyName,ParameterValue='id_rsa'
        else
            echo "Spinning up regional stack for us-east-1"
            aws cloudformation create-stack --region us-east-1 --stack-name $STACK_NAME-regional --template-body file://cloudformation/regional_infrastructure.yaml --parameters ParameterKey=KeyName,ParameterValue='id_rsa'
        fi


        ;;

        spin-down)

        echo "Getting the name of the CodePipeline S3 Bucket"
        codepipeline_bucket_physical_name=$(aws cloudformation --region eu-west-1 list-stack-resources --stack-name $STACK_NAME --query 'StackResourceSummaries[?LogicalResourceId==`CodePipelineS3Bucket`].[PhysicalResourceId]' --output=text)

        if [ -n "$codepipeline_bucket_physical_name" ]; then
            echo "Emptying the CodePipeline S3 bucket"
            pip install boto3 > /dev/null
            python empty_bucket.py $codepipeline_bucket_physical_name
        else
            echo "CodePipeline S3 Bucket already deleted"
        fi

        echo "Terminating stack $STACK_NAME"
        aws cloudformation delete-stack \
            --stack-name $STACK_NAME \
            --region $BASE_REGION

        echo "Terminating regional stack $STACK_NAME-regional in eu-west-1"
        aws cloudformation delete-stack --region eu-west-1 --stack-name $STACK_NAME-regional

        echo "Terminating regional stack $STACK_NAME-regional in us-east-1"
        aws cloudformation delete-stack --region us-east-1 --stack-name $STACK_NAME-regional

        echo "Emptying template bucket..."
        python empty_bucket.py msv-templates

        echo "Terminating template bucket..."
        aws s3 rb s3://msv-templates

        ;;
        esac
exit 0
