#!/bin/sh
source venv/bin/activate
flask init-db
exec gunicorn -b :5000 --access-logfile - --error-logfile - --log-level debug --timeout 60 --workers 2 server:app

