FROM node:16.14.2

WORKDIR /usr/src/frontdoor

# TODO: Install packages with yarn from npm registry (yarn needs .npmrc for auth)
COPY package.json yarn.lock ./
ARG NPM_CONFIG_REGISTRY
ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc \
  && echo "\"registry\" \"${NPM_CONFIG_REGISTRY}\"" > .yarnrc \
  && yarn install

# Copy files
COPY . .

# Secrets
# TODO: move to runtime from layers
# ARG AWS_REGION
# ENV AWS_REGION=$AWS_REGION
# ARG AWS_ACCESS_KEY_ID
# ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
# ARG AWS_SECRET_ACCESS_KEY
# ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
# ARG NODE_ENV
# ENV NODE_ENV=$NODE_ENV

# Start
EXPOSE 1110
CMD ["yarn", "preview"]
