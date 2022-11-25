#!/bin/bash -x
# set -e will abort this script on non-zero exist codes. Ex) Jest error is a 1
set -e

# //////////////////////////////////////////////////////////////////////////////
# Variables
# //////////////////////////////////////////////////////////////////////////////
GIDEON_PATH="$PWD"
CPU_CHIP=$(bash "${GIDEON_PATH}/ops/get-cpu-chip.sh" $*)
echo "CPU: ${CPU_CHIP}"

TARGET=$1
if [[ $TARGET == "production" ]]
then
  echo "Recognized Environment: '${TARGET}'"
  source ./.env
elif [[ $TARGET == "development" ]]
then
  echo "Recognized Environment: '${TARGET}'"
  source ./.env
elif [[ $TARGET == "staging" ]]
then
  echo "Recognized Environment: '${TARGET}'"
  source ./.env
else
  echo "Unrecognized Environment: '${TARGET}'"
  exit 1
fi
NODE_ENV=$TARGET

GIT_SHA="$(git rev-parse HEAD)"
GIDEON_FRONTEND_DEFENDER_BUILD_PATH="$GIDEON_PATH/frontends/defender/dist"
GIDEON_FRONTEND_DEFENDER_PATH="$GIDEON_PATH/frontends/defender"
GIDEON_FRONTEND_FRONTDOOR_BUILD_PATH="$GIDEON_PATH/frontends/frontdoor/dist"
GIDEON_FRONTEND_FRONTDOOR_PATH="$GIDEON_PATH/frontends/frontdoor"

UNDERLINE='\033[4;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[1;31m'
NC='\033[0m'

# //////////////////////////////////////////////////////////////////////////////
# Common Functions
# //////////////////////////////////////////////////////////////////////////////
function confirm_command () {
  # Remind of environment
  echo -e "Env: ${UNDERLINE}${TARGET}${NC}"
  # Remind of command
  if [[ -n "$1" ]]
  then
    echo -e "Cmd: ${UNDERLINE}deploy.sh ${1} ${2} ${3} ${4}${NC}\n"
  fi
  # Confirm
  read -p "Are you sure? [Y/n] " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Y]$ ]]
  then
    echo -e "${GREEN}Running${NC}\n"
  else
    echo -e "${RED}Aborting${NC}\n"
    exit 0
  fi
}

function confirm_finish() {
  echo -e "\n${GREEN}deploy.sh - Finished${NC}\n"
}

function get_secret {
  echo $(bash "${GIDEON_PATH}/ops/get-secret.sh" $TARGET $1)
}

function eval_aws () {
  # Vars
  AWS_ACCOUNT_ID=$(get_secret ".AWS_ACCOUNT_ID")
  AWS_REGION=$(get_secret ".AWS_REGION")
  # Eval
  AWS_ECR_PASSWORD="$(aws ecr get-login-password --profile gideon --region $AWS_REGION)"
  docker login \
    --username AWS \
    --password $AWS_ECR_PASSWORD \
    "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
}

# //////////////////////////////////////////////////////////////////////////////
# Build Functions
# //////////////////////////////////////////////////////////////////////////////

# Frontend webpack build handling for coordinator, frontend_frontdoor, partners
function build_frontend_spa () {
  # Vars
  AWS_REGION=$(get_secret ".AWS_REGION")
  # Install in case of package updates
  yarn install
  # Build
  NODE_ENV=$NODE_ENV \
    AWS_REGION=$AWS_REGION \
    AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    yarn run build:production
}

function build_frontend_defender () {
  cd "${GIDEON_FRONTEND_DEFENDER_PATH}"
  build_frontend_spa
  cd -
}

function build_frontend_frontdoor () {
  cd "${GIDEON_FRONTEND_FRONTDOOR_PATH}"
  build_frontend_spa
  cd -
}

# //////////////////////////////////////////////////////////////////////////////
# Push Functions
# //////////////////////////////////////////////////////////////////////////////

function push_frontend_defender() {
  # Vars
  # Build
  aws s3 sync "${GIDEON_FRONTEND_DEFENDER_BUILD_PATH}" s3://${GIDEON_FRONTEND_DEFENDER_BUCKET} \
    --acl public-read \
    --delete \
    --cache-control "public,max-age=300" \
    --profile gideon
}

function push_frontend_frontdoor() {
  # Vars
  # Build
  aws s3 sync "${GIDEON_FRONTEND_FRONTDOOR_BUILD_PATH}" s3://${GIDEON_FRONTEND_FRONTDOOR_BUCKET} \
    --acl public-read \
    --delete \
    --cache-control "public,max-age=300" \
    --profile gideon
}


# //////////////////////////////////////////////////////////////////////////////
# Cache Busting Functions
# //////////////////////////////////////////////////////////////////////////////

function bust_frontend_defender() {
  # Vars
  # Bust
  aws configure set preview.cloudfront true --profile gideon
  aws cloudfront create-invalidation --distribution-id ${GIDEON_FRONTEND_DEFENDER_CLOUDRONT_DIST_ID} --paths "/*" --profile gideon
}

function bust_frontend_frontdoor() {
  # Vars
  # Bust
  aws configure set preview.cloudfront true --profile gideon
  aws cloudfront create-invalidation --distribution-id ${GIDEON_FRONTEND_FRONTDOOR_CLOUDRONT_DIST_ID} --paths "/*" --profile gideon
}

# //////////////////////////////////////////////////////////////////////////////
# Task/Service Functions
# //////////////////////////////////////////////////////////////////////////////



# //////////////////////////////////////////////////////////////////////////////
# Run
# //////////////////////////////////////////////////////////////////////////////
echo -e "${GREEN}deploy.sh - Started${NC}"
COMMAND=$2
OPTION_ONE=$3
OPTION_TWO=$4

# Execute command
case "${COMMAND}" in
  frontends_defender)
  confirm_command $COMMAND $OPTION_ONE
  build_frontend_defender
  push_frontend_defender
  bust_frontend_defender
  confirm_finish
  exit 0
  ;;
  frontends_frontdoor)
  confirm_command $COMMAND $OPTION_ONE
  build_frontend_frontdoor
  push_frontend_frontdoor
  bust_frontend_frontdoor
  confirm_finish
  exit 0
  ;;
  *)
  echo "Unrecognized Service: '${2}'"
  exit 1
  ;;
esac
# Done
exit 0
