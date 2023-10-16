#! /usr/bin/env bash

# Let the DB start
python backend/backend_pre_start.py

# Run migrations
# TODO uncoment here when alembic'll be added
# alembic upgrade head

# Create initial data in DB
python backend/initial_data.py
