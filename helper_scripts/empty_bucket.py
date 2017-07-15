#!/usr/bin/python

import sys
import boto3

BUCKET = sys.argv[1]

s3 = boto3.resource('s3', region_name='eu-west-1')
bucket = s3.Bucket(BUCKET)
bucket.object_versions.delete()
