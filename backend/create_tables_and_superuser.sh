#! /usr/bin/env bash
export PYTHONPATH='/code'
# Let the DB start
python backend_pre_start.py

# Run migrations
# TODO uncoment here when alembic'll be added
alembic upgrade head

# Create initial data in DB
python initial_data.py
