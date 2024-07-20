#!/bin/bash

GIT_VERSION=$(git rev-parse HEAD)

pytest tests/ -v --pact-broker-url=${PACT_BROKER_BASE_URL} --pact-provider-name=google-login-back --pact-publish-results --pact-provider-version=${GIT_VERSION}
