#!/bin/sh


set -ex # fail on any error and enable print of debug logs

python manage.py migrate # Migrate DB
python manage.py collectstatic --noinput # Collect static
python manage.py runserver 0.0.0.0:8005 # Run application
