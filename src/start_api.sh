#!/bin/bash

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn --chdir simple_api --bind :8000 simple_api.wsgi:application