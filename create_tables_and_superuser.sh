#! /usr/bin/env bash
export PYTHONPATH='/code'
# Let the DB start
python backend/backend_pre_start.py

cd backend/
# Run migrations
# TODO uncoment here when alembic'll be added
alembic upgrade head

cd ..
# Create initial data in DB
python backend/initial_data.py
