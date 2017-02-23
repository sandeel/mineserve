#!/bin/bash

echo "Getting the name of the CodePipeline S3 Bucket"
codepipeline_bucket_physical_name=$(aws cloudformation --region eu-west-1 list-stack-resources --stack-name msv --query 'StackResourceSummaries[?LogicalResourceId==`CodePipelineS3Bucket`].[PhysicalResourceId]' --output=text)

if [ -n "$codepipeline_bucket_physical_name" ]; then
    echo "Emptying the CodePipeline S3 bucket"
    aws s3 rm s3://$codepipeline_bucket_physical_name --recursive
else
    echo "CodePipeline S3 Bucket already deleted"
fi

aws cloudformation delete-stack \
    --stack-name msv-master \
    --region eu-west-1

aws cloudformation delete-stack \
    --stack-name msv-development \
    --region eu-west-1
