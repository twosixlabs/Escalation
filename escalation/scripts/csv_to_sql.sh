#!/bin/sh

# This script is run from the host machine, in the top level directory of the repo, using the Docker containers built to create sql tables from csv
# usage: . csv_to_sql.sh {sql_table_name} {path to csv file machine running script} {replace/append/fail}
# e.g.:
# . csv_to_sql.sh structural_metrics /Users/nick.leiby/repos/versioned-datasets/data/protein-design/structural_metrics/topology_mining_and_Longxing_chip_1.v1.structural_metrics.csv replace


if [[ ! -d  "$(pwd)/escalation/app_deploy_data" ]]; then
  echo "Script must be run from the top directory of the Escalation code repository"
  exit 1
fi


table_name=$1
data_file_path=$2

if [[ "$3" =~ ^(replace|append|fail)$ ]]; then
    table_exists_behavior=$3
else
    echo "table_exists_behavior is unset, or set with an invalid option. Should be one of: replace,append,fail"
    exit 1
fi

if [[ -z "${table_name}" ]]; then
    echo "table_name is unset or set to the empty string"
    exit 1
fi

if [[ -z "${data_file_path}" ]]; then
    echo "data_file_path is unset or set to the empty string"
    exit 1
fi


echo "Aliasing $data_file_path on host to /escalation/data.csv on Docker container"
echo "Adding data to $table_name with $table_exists_behavior behavior if it exists"

docker-compose run \
--entrypoint "python csv_to_sql.py $1 /escalation/data.csv $3" \
-v $2:/escalation/data.csv \
-v "$(pwd)/escalation/app_deploy_data/models.py:/escalation/app_deploy_data/models.py" \
web