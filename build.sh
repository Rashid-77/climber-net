#! /usr/bin/env sh

# Exit in case of error
set -e

mkdir -p 'log'
docker compose \
-f docker-compose.yml \
build
