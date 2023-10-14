FROM postgres:15.0-alpine
COPY ./db_init/table/ /docker-entrypoint-initdb.d/