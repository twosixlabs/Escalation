#!/usr/bin/env bash


if [[ ! -d  "$(pwd)/escalation/app_deploy_data" ]]; then
  echo "Script must be run from the top directory of the Escalation code repository"
  exit 1
fi

read -p "This will reset the Docker db volume to an initial blank state. Are you sure? Enter [Y] to confirm" -n 1 -r
echo # move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "running"
    echo "docker-compose down --volumes"
    docker-compose down --volumes
    echo "Resetting models.py"
    cp escalation/database/models_template.py escalation/app_deploy_data/models.py
else
    echo "Aborting- no action taken"
fi
