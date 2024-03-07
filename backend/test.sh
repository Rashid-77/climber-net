#! /usr/bin/env sh

# Exit in case of error
set -e

docker compose \
-f test.docker-compose.yml \
config > docker-stack.yml

docker compose -f docker-stack.yml build
# Remove possibly previous broken stacks left hanging after an error
docker compose -f docker-stack.yml down -v --remove-orphans 
docker compose -f docker-stack.yml up -d
docker exec -it climb-net bash /code/tests/test-start.sh "$@"
docker compose -f docker-stack.yml down -v --remove-orphans