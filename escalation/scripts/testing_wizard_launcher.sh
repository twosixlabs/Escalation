#!/usr/bin/env bash
# This script is called by the user from the Host machine, and it launches the app in debug mode in a container
# launch the web app using a debug mode,
# mounting the app_deploy data directly in order to monitor and relaunch when changed by the config wizard

if [[ ! -d  "$(pwd)/escalation/app_deploy_data" ]]; then
  echo "Script must be run from the top directory of the Escalation code repository"
  exit 1
fi

docker-compose run --entrypoint /escalation/scripts/boot_escalation_debug_mode.sh \
-p "8000:8000" \
-v "$(pwd)/escalation/app_deploy_data":/escalation/app_deploy_data \
-v "$(pwd)/escalation/templates/:/escalation/templates/" \
-e FLASK_DEBUG=true \
-e DATABASE_CONFIG="postgresql+psycopg2://escalation:escalation_pwd@postgres_db:5432/testing_escalation" \
web

