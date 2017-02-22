#!/bin/bash

stack_exists=`aws cloudformation --region $BASE_REGION describe-stacks --stack-name $BASE_STACK_NAME`
stack_status=$(echo $stack_exists | jq '.Stacks[0].StackStatus')

if [ "$stack_status" == "\"CREATE_COMPLETE\"" ]; then
    echo "Stack already deleted".
    exit 0
fi


echo "Getting the name of the CodePipeline S3 Bucket"
codepipeline_bucket_physical_name=$(aws cloudformation --region eu-west-1 list-stack-resources --stack-name msv --query 'StackResourceSummaries[?LogicalResourceId==`CodePipelineS3Bucket`].[PhysicalResourceId]' --output=text)

if [ -n "$codepipeline_bucket_physical_name" ]; then
    echo "Emptying the CodePipeline S3 bucket"
    aws s3 rm s3://$codepipeline_bucket_physical_name --recursive
else
    echo "CodePipeline S3 Bucket already deleted"
fi

aws cloudformation delete-stack \
    --stack-name msv \
    --region eu-west-1
