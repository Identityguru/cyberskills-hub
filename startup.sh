#!/bin/bash
set -e

echo "Running database seed/migrations..."
python3 seed/seed.py

echo "Starting CyberSkills Hub..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}" --workers 1
