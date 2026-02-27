#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Please provide a migration message."
  echo "Usage: ./migrate.sh \"your message\""
  exit 1
fi

echo "Creating migration..."
alembic revision --autogenerate -m "$1"

echo "Upgrading database..."
alembic upgrade head

echo "Done!"