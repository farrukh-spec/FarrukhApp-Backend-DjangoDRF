#!/bin/sh

# If any command fails, stop the script
set -e

echo "Waiting for postgres..."
# This loop checks if the DB port is open
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations automatically every time the container starts
python manage.py migrate

# Execute the CMD from the Dockerfile (Gunicorn)
exec "$@"