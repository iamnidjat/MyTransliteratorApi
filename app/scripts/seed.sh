#!/bin/bash
set -e

echo "Seeding the db with dummy data..."
python -m app.utils.dev_seed

echo "Done!"