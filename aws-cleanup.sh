#!/usr/bin/env bash
set -e

echo "[aws-cleanup] Cleanup $environment_name..."

# disable AWS CLI pager
export AWS_PAGER=""

sam delete --no-prompts --stack-name "$environment_name" --region "$AWS_DEFAULT_REGION"
