#!/bin/bash -x
# set -e will abort this script on non-zero exist codes. Ex) Jest error is a 1
set -e

# //////////////////////////////////////////////////////////////////////////////
# Variables
# //////////////////////////////////////////////////////////////////////////////
GIDEON_PATH="$PWD"
CPU_CHIP=$(bash "${GIDEON_PATH}/ops/get-cpu-chip.sh" $*)
echo "CPU: ${CPU_CHIP}"

TARGET_ENV=$1
if [[ $TARGET_ENV == "production" ]]
then
  echo "Recognized Environment: '${TARGET_ENV}'"
  source ./.env
elif [[ $TARGET_ENV == "development" ]]
then
  echo "Recognized Environment: '${TARGET_ENV}'"
  source ./.env
elif [[ $TARGET_ENV == "staging" ]]
then
  echo "Recognized Environment: '${TARGET_ENV}'"
  source ./.env
else
  echo "Unrecognized Environment: '${TARGET_ENV}'"
  exit 1
fi

GIT_SHA="$(git rev-parse HEAD)"
GIDEON_API_PATH="$GIDEON_PATH/backends"
GIDEON_API_NGINX_PATH="$GIDEON_PATH/ops/apiNginx"
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
  echo -e "Env: ${UNDERLINE}${TARGET_ENV}${NC}"
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
  echo $(bash "${GIDEON_PATH}/ops/get-secret.sh" $TARGET_ENV $1)
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

function build_api () {
  cd "${GIDEON_API_PATH}"
  # Vars
  AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
  AWS_ECR_REGISTRY=$(get_secret ".AWS_ECR_REGISTRY")
  AWS_REGION=$(get_secret ".AWS_REGION")
  AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
  DOCKER_IMAGE_NAME_API=$(get_secret ".DOCKER_IMAGE_NAME_API")
  # Build
  docker build -t "${DOCKER_IMAGE_NAME_API}:${GIT_SHA}" \
    --build-arg "AWS_REGION=$AWS_REGION" \
    --build-arg "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" \
    --build-arg "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" \
    --build-arg "TARGET_ENV=$TARGET_ENV" \
    --network gideon_default \
    --label "registry=$AWS_ECR_REGISTRY" \
    .
  cd -
}

# Build API's NGINX reverse proxy
function build_api_nginx () {
  cd "${GIDEON_API_NGINX_PATH}"
  # Vars
  DOCKER_IMAGE_NAME_API_NGINX=$(get_secret ".DOCKER_IMAGE_NAME_API_NGINX")
  # Build
  docker build -t "${DOCKER_IMAGE_NAME_API_NGINX}:latest" .
  cd -
}

# Frontend webpack build handling for coordinator, frontend_frontdoor, partners
function build_frontend_spa () {
  # Vars
  AWS_REGION=$(get_secret ".AWS_REGION")
  # Install in case of package updates
  yarn install
  # Build
  TARGET_ENV=$TARGET_ENV \
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
  GIDEON_FRONTEND_DEFENDER_BUCKET=$(get_secret ".GIDEON_FRONTEND_DEFENDER_BUCKET")
  aws s3 sync "${GIDEON_FRONTEND_DEFENDER_BUILD_PATH}" s3://${GIDEON_FRONTEND_DEFENDER_BUCKET} \
    --acl public-read \
    --delete \
    --cache-control "public,max-age=300" \
    --profile gideon
}

function push_frontend_frontdoor() {
  GIDEON_FRONTEND_FRONTDOOR_BUCKET=$(get_secret ".GIDEON_FRONTEND_FRONTDOOR_BUCKET")
  aws s3 sync "${GIDEON_FRONTEND_FRONTDOOR_BUILD_PATH}" s3://${GIDEON_FRONTEND_FRONTDOOR_BUCKET} \
    --acl public-read \
    --delete \
    --cache-control "public,max-age=300" \
    --profile gideon
}

function push_api_image () {
  # Vars
  AWS_ECR_REGISTRY=$(get_secret ".AWS_ECR_REGISTRY")
  AWS_ECR_REPO_API=$(get_secret ".AWS_ECR_REPO_API")
  DOCKER_IMAGE_NAME_API=$(get_secret ".DOCKER_IMAGE_NAME_API")
  # Tag/Push
  docker tag "${DOCKER_IMAGE_NAME_API}:${GIT_SHA}" "${AWS_ECR_REGISTRY}/${AWS_ECR_REPO_API}:${GIT_SHA}"
  docker push "${AWS_ECR_REGISTRY}/${AWS_ECR_REPO_API}:${GIT_SHA}"
}

function push_api_nginx_image () {
  # Vars
  AWS_ECR_REGISTRY=$(get_secret ".AWS_ECR_REGISTRY")
  AWS_ECR_REPO_API_NGINX=$(get_secret ".AWS_ECR_REPO_API_NGINX")
  DOCKER_IMAGE_NAME_API_NGINX=$(get_secret ".DOCKER_IMAGE_NAME_API_NGINX")
  # Tag/Push
  docker tag "${DOCKER_IMAGE_NAME_API_NGINX}:latest" "${AWS_ECR_REGISTRY}/${AWS_ECR_REPO_API_NGINX}:latest"
  docker push "${AWS_ECR_REGISTRY}/${AWS_ECR_REPO_API_NGINX}"
}


# //////////////////////////////////////////////////////////////////////////////
# Cache Busting Functions
# //////////////////////////////////////////////////////////////////////////////

function bust_frontend_defender() {
  GIDEON_FRONTEND_DEFENDER_CLOUDRONT_DIST_ID=$(get_secret ".GIDEON_FRONTEND_DEFENDER_CLOUDRONT_DIST_ID")
  aws configure set preview.cloudfront true --profile gideon
  aws cloudfront create-invalidation --distribution-id ${GIDEON_FRONTEND_DEFENDER_CLOUDRONT_DIST_ID} --paths "/*" --profile gideon
}

function bust_frontend_frontdoor() {
  GIDEON_FRONTEND_FRONTDOOR_CLOUDRONT_DIST_ID=$(get_secret ".GIDEON_FRONTEND_FRONTDOOR_CLOUDRONT_DIST_ID")
  aws configure set preview.cloudfront true --profile gideon
  aws cloudfront create-invalidation --distribution-id ${GIDEON_FRONTEND_FRONTDOOR_CLOUDRONT_DIST_ID} --paths "/*" --profile gideon
}

# //////////////////////////////////////////////////////////////////////////////
# Task/Service Functions
# //////////////////////////////////////////////////////////////////////////////

function update_api_task () {
  cd "${GIDEON_PATH}"
  # Vars
  AWS_EXECUTION_ROLE_ARN=$(get_secret ".AWS_EXECUTION_ROLE_ARN")
  AWS_REGION=$(get_secret ".AWS_REGION")
  AWS_ECR_REGISTRY=$(get_secret ".AWS_ECR_REGISTRY")
  AWS_ECR_REPO_API_NGINX=$(get_secret ".AWS_ECR_REPO_API_NGINX")
  AWS_ECR_REPO_API=$(get_secret ".AWS_ECR_REPO_API")
  AWS_ECS_TASK_API=$(get_secret ".AWS_ECS_TASK_API")
  AWS_ECS_TASK_API_CPU=$(get_secret ".AWS_ECS_TASK_API_CPU")
  AWS_ECS_TASK_API_MEMORY=$(get_secret ".AWS_ECS_TASK_API_MEMORY")
  # Setup
  API_IMAGE_TARGET="$AWS_ECR_REGISTRY/$AWS_ECR_REPO_API:$GIT_SHA"
  API_NGINX_IMAGE_TARGET="$AWS_ECR_REGISTRY/$AWS_ECR_REPO_API_NGINX:latest"
  GIDEON_API_PORT=$(get_secret ".GIDEON_API_PORT")
  DOCKER_IMAGE_NAME_API=$(get_secret ".DOCKER_IMAGE_NAME_API")
  CONTAINER_DEFINITION_API="{\"name\":\"$DOCKER_IMAGE_NAME_API\",\"image\":\"$API_IMAGE_TARGET\",\"essential\":true,\"memoryReservation\":995,\"portMappings\":[{\"containerPort\":$GIDEON_API_PORT,\"hostPort\":$GIDEON_API_PORT}],\"dependsOn\":[],\"logConfiguration\":{\"logDriver\":\"awslogs\",\"options\":{\"awslogs-group\":\"/ecs/api/api\",\"awslogs-region\":\"us-east-1\",\"awslogs-stream-prefix\":\"ecs\"}}}"
  CONTAINER_DEFINITION_NGINX="{\"name\":\"nginx\",\"image\":\"$API_NGINX_IMAGE_TARGET\",\"essential\":true,\"cpu\":256,\"memory\":100,\"portMappings\":[{\"hostPort\":80,\"protocol\":\"tcp\",\"containerPort\":80}],\"dependsOn\":[],\"logConfiguration\":{\"logDriver\":\"awslogs\",\"options\":{\"awslogs-group\":\"/ecs/api/nginx\",\"awslogs-region\":\"us-east-1\",\"awslogs-stream-prefix\":\"ecs\"}}}"
  # Run
  aws ecs register-task-definition \
    --family $AWS_ECS_TASK_API \
    --container-definitions "[$CONTAINER_DEFINITION_API,$CONTAINER_DEFINITION_NGINX]" \
    --requires-compatibilities 'FARGATE' \
    --cpu $AWS_ECS_TASK_API_CPU \
    --memory $AWS_ECS_TASK_API_MEMORY \
    --network-mode 'awsvpc' \
    --task-role-arn $AWS_EXECUTION_ROLE_ARN \
    --execution-role-arn $AWS_EXECUTION_ROLE_ARN \
    --profile gideon
  cd -
}

function update_api_service () {
  cd "${GIDEON_PATH}"
  # Vars
  AWS_ECS_CLUSTER=$(get_secret ".AWS_ECS_CLUSTER")
  AWS_ECS_SERVICE_API=$(get_secret ".AWS_ECS_SERVICE_API")
  AWS_ECS_TASK_API=$(get_secret ".AWS_ECS_TASK_API")
  # Update
  aws ecs update-service \
    --cluster $AWS_ECS_CLUSTER \
    --service $AWS_ECS_SERVICE_API \
    --task-definition $AWS_ECS_TASK_API \
    --profile gideon
  cd -
}

# //////////////////////////////////////////////////////////////////////////////
# Run
# //////////////////////////////////////////////////////////////////////////////
echo -e "${GREEN}deploy.sh - Started${NC}"
COMMAND=$2
OPTION_ONE=$3
OPTION_TWO=$4

# Execute command
case "${COMMAND}" in
  backends_api)
  confirm_command $COMMAND $OPTION_ONE
  build_api
  eval_aws
  push_api_image
  update_api_task
  update_api_service
  confirm_finish
  exit 0
  ;;
  backends_api_nginx)
  confirm_command $COMMAND $OPTION_ONE
  build_api_nginx
  eval_aws
  push_api_nginx_image
  confirm_finish
  exit 0
  ;;
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
