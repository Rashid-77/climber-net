#! /usr/bin/env sh

# Exit in case of error
set -e

mkdir -p 'dialog_svc/log'
docker compose \
-f dialog_svc/docker-compose.yml \
build
