#!/bin/bash

BASE_REGION=eu-west-1
ALL_REGIONS=( eu-west-1 us-east-1 us-east-2 us-west-2 ap-southeast-2 )
BASE_STACK_NAME=msv


echo ${ALL_REGIONS[1]}

# --- do not change ---
GIT_BRANCH=$(git symbolic-ref --short -q HEAD)
STACK_NAME=$BASE_STACK_NAME-$GIT_BRANCH
#----------------------

key="$1"
case $key in
        spin-up)

        echo "Note: this will spin up a stack for the current Git branch ($GIT_BRANCH)."

        : ${MSV_GITHUB_TOKEN?"Need to set MSV_GITHUB_TOKEN. Try running with MSV_GITHUB_TOKEN=xyz123 ./spin-up.sh"}

        echo "Creating bucket for CloudFormation templates..."
        aws s3 mb s3://msv-templates

        echo "Uploading ark template..."
        aws s3 cp modules/ark/cloudformation/regional.yaml s3://msv-templates/ark/regional.yaml

        aws cloudformation \
            --region $BASE_REGION \
            deploy \
            --stack-name $STACK_NAME \
            --template-file cloudformation/cloudformation.yaml \
            --parameter-overrides GitBranch=$GIT_BRANCH \
                                  KeyPair=id_rsa \
                                  FlaskDebug=False \
                                  GithubToken=$MSV_GITHUB_TOKEN \
                                  StripePublishableKey=$MSV_STRIPE_PK \
                                  StripeSecretKey=$MSV_STRIPE_SK \
                                  AdminPassword=$MSV_ADMIN_PASS \
                                  Beta=True \
            --capabilities CAPABILITY_IAM

        for REGION in "${ALL_REGIONS[@]}"
        do
            aws cloudformation deploy \
                --region $REGION \
                --stack-name $STACK_NAME-regional
                --template-file cloudformation/regional_infrastructure.yaml --parameters ParameterKey=KeyName,ParameterValue='id_rsa'
        done
        ;;

        spin-down)

        pip install boto3 > /dev/null

        echo "Getting the name of the CodePipeline S3 Bucket"
        codepipeline_bucket_physical_name=$(aws cloudformation --region eu-west-1 list-stack-resources --stack-name $STACK_NAME --query 'StackResourceSummaries[?LogicalResourceId==`CodePipelineS3Bucket`].[PhysicalResourceId]' --output=text)

        if [ -n "$codepipeline_bucket_physical_name" ]; then
            echo "Emptying the CodePipeline S3 bucket"
            python empty_bucket.py $codepipeline_bucket_physical_name
        else
            echo "CodePipeline S3 Bucket already deleted"
        fi

        echo "Getting the name of the Frontend S3 Bucket"
        codepipeline_bucket_physical_name=$(aws cloudformation --region eu-west-1 list-stack-resources --stack-name $STACK_NAME --query 'StackResourceSummaries[?LogicalResourceId==`FrontendBucket`].[PhysicalResourceId]' --output=text)

        if [ -n "$codepipeline_bucket_physical_name" ]; then
            echo "Emptying theFrontend S3 bucket"
            python empty_bucket.py $codepipeline_bucket_physical_name
        else
            echo "Frontend S3 Bucket already deleted"
        fi


        echo "Terminating regional resources..."
        for REGION in "${ALL_REGIONS[@]}"
        do
            echo "Checking for container instances to terminate in $REGION"
            for instance in `aws ec2 describe-instances --filters "Name=tag:Name,Values=msv-container-*" --region $REGION | jq -r '.Reservations[].Instances[].InstanceId'`
            do
                echo "Terminating $instance..."
                aws ec2 terminate-instances --region $REGION --instance-ids $instance
            done

            echo "Terminating regional stack $STACK_NAME-regional in $REGION"
            aws cloudformation delete-stack --region $REGION --stack-name $STACK_NAME-regional

        done

        echo "Emptying template bucket..."
        python empty_bucket.py msv-templates

        echo "Terminating template bucket..."
        aws s3 rb s3://msv-templates

        echo "All manual resource terminations complete. CloudFormation stacks will now spin down."

        echo "Terminating stack $STACK_NAME"
        aws cloudformation delete-stack \
            --stack-name $STACK_NAME \
            --region $BASE_REGION

        echo "Deleting repos..."
        aws ecr delete-repository --region $BASE_REGION --repository-name $BASE_STACK_NAME-frontend --force

        ;;
        esac
exit 0
