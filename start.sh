#!/bin/sh
set -e

echo "--- Running database migrations..."
python -m app.migrate

echo "--- Starting the bot..."
python -m app.main
