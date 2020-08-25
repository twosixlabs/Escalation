#!/bin/sh
exec gunicorn -b 0.0.0.0:8000 --access-logfile - --error-logfile - --log-level debug --timeout 1200 --workers 2 app:app

