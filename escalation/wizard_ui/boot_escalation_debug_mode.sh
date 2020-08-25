#!/usr/bin/env bash
# todo: assert that this is run from the top level of the repo

# this watches for changes in the app_deploy_data directory, relaunching the flask app if there are any
export FLASK_ENV=development
export DEBUG=true
export FLASK_RUN_EXTRA_FILES="/escalation/app_deploy_data/"
flask run --host=0.0.0.0 --port=8000 --extra-files $FLASK_RUN_EXTRA_FILES