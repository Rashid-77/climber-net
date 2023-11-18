#! /usr/bin/env sh

# Exit in case of error
set -e

mkdir -p 'backend/log'
docker compose \
-f backend/docker-compose.yml \
build
