#!/bin/bash

# Build the project
echo "Building the project..."
python -m pip install -r requirements.txt

# Make migrations
echo "Making migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput