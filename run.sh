#!/bin/sh


set -e # fail on any error
set -x # enable print of debug logs

cd /code/

python manage.py migrate # Migrate DB
python manage.py collectstatic # Collect static
python manage.py runserver 0.0.0.0:8005 # Run application
