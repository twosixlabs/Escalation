#!/bin/sh
source venv/bin/activate
flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - --log-level debug --timeout 1200 --workers 4 server:app

