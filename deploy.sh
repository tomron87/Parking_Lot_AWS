#!/bin/bash

sam build
sam deploy --guided \
  --stack-name parking-lot-hw1 \
  --s3-bucket parking-lot-grader-bucket \
  --region eu-central-1