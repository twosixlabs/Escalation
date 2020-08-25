#!/usr/bin/env bash
# This script is called by the user from the Host machine, and it launches the wizard app in debug mode in a container

if [[ ! -d  "$(pwd)/escalation/app_deploy_data" ]]; then
  echo "Script must be run from the top directory of the Escalation code repository"
  exit 1
fi

docker-compose run --entrypoint /escalation/wizard_ui/boot_wizard_app.sh -p "8001:8001"  -v "$(pwd)/escalation/app_deploy_data":/escalation/app_deploy_data web


