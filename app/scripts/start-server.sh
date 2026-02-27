#!/bin/bash
set -e

echo "Starting FastAPI server..."
uvicorn app.main:app --reload
