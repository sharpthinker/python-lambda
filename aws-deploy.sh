#!/usr/bin/env bash
set -e

echo "[aws-deploy] Deploy $appname..."

# disable AWS CLI pager
export AWS_PAGER=""

# try to create bucket if it doesn't exist yet
if ! aws s3 ls "$AWS_SAM_BUCKET"
then
  echo "SAM bucket ($AWS_SAM_BUCKET) not found: try to create..."
  aws s3api create-bucket --bucket "$AWS_SAM_BUCKET" --region "$AWS_DEFAULT_REGION"
fi

# 1: build
sam build ${TRACE+--debug}

# 2: deploy (each environment is a separate stack)
# AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY defined as secret CI/CD variable
# AWS_DEFAULT_REGION and AWS_SAM_BUCKET defined as project CI/CD variable
sam deploy ${TRACE+--debug} \
  --stack-name "$appname" \
  --region "$AWS_DEFAULT_REGION" \
  --s3-bucket "$AWS_SAM_BUCKET" \
  --no-fail-on-empty-changeset \
  --no-confirm-changeset \
  --parameter-overrides "AppName=$appname HostedZoneId=$AWS_HOSTED_ZONE_ID CustomDomainCertArn=$AWS_CUSTOM_DOMAIN_CERT_ARN" \
  --tags "ci-job-url=$CI_JOB_URL environment=$env"

# Retrieve outputs (use cloudformation query)
api_url=$(aws cloudformation describe-stacks --stack-name "$appname" --output text --query 'Stacks[0].Outputs[?OutputKey==`BurgerApiUrl`].OutputValue')

echo "Stack created/updated:"
echo " - Api URL: $api_url"

# Finally set the dynamically generated WebServer Url
echo "$api_url" > environment_url.txt
