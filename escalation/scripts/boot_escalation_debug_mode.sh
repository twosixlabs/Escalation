#!/usr/bin/env bash
# this watches for changes in the app_deploy_data directory, relaunching the flask app if there are any
export FLASK_ENV=development
export FLASK_RUN_EXTRA_FILES="/escalation/app_deploy_data/:/escalation/templates/"
flask run --host=0.0.0.0 --port=8000 --extra-files $FLASK_RUN_EXTRA_FILES