#!/bin/bash
SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"admin@scoutifii.com"}

cd /app/

/opt/venv/bin/python manage.py migrate
/opt/venv/bin/python manage.py createsuperuser --email $SUPERUSER_EMAIL --noinput || true