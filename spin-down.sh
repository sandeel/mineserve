#!/bin/bash

aws cloudformation delete-stack \
    --stack-name msv \
    --region eu-west-1
