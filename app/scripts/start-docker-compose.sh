#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Seeding data..."
python -m app.utils.dev_seed

echo "Starting app..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload