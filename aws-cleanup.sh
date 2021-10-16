#!/usr/bin/env bash
set -e

echo "[aws-cleanup] Cleanup $appname..."

# disable AWS CLI pager
export AWS_PAGER=""

sam delete --no-prompts --stack-name "$appname" --region "$AWS_DEFAULT_REGION"
