#!/bin/bash -x
set -e

# Args for secret picking
TARGET=$1
JQ_PATH=$2

# Output (can't 'return' like a JS function. Bash expects piping streams)
echo $(aws secretsmanager get-secret-value --secret-id ${TARGET} --profile gideon | jq -r '.SecretString' | jq -r ${JQ_PATH})
