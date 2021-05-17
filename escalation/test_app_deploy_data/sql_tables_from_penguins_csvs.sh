#!/usr/bin/env bash

if [[ ! -d  "$(pwd)/app_deploy_data" ]]; then
  echo "Script must be run from the top directory of the Escalation code repository"
  exit 1
fi

TESTING_DATABASE=testing_escalation
MAIN_DATABASE=escalation
# write to the TESTING database.
export SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://escalation:escalation_pwd@localhost:5432/$TESTING_DATABASE

python scripts/csv_to_sql.py miserables_edges test_app_deploy_data/data/miserables_edges/miserables_edges.csv replace setup_script "test setup"
python scripts/csv_to_sql.py miserables_nodes test_app_deploy_data/data/miserables_nodes/miserables_nodes.csv replace setup_script "test setup"
python scripts/csv_to_sql.py temperature test_app_deploy_data/data/temperature/temperature.csv replace setup_script "test setup"
python scripts/csv_to_sql.py penguin_size test_app_deploy_data/data/penguin_size/penguin_size.csv replace setup_script "test setup"
python scripts/csv_to_sql.py penguin_size test_app_deploy_data/data/penguin_size/penguin_size_2.csv append setup_script "test setup"
python scripts/csv_to_sql.py mean_penguin_stat test_app_deploy_data/data/mean_penguin_stat/mean_penguin_stat.csv replace setup_script "test setup"
python scripts/csv_to_sql.py penguin_size_small test_app_deploy_data/data/penguin_size_small/penguin_size_small.csv replace setup_script "test setup"
python scripts/csv_to_sql.py penguin_lter_small test_app_deploy_data/data/penguin_lter_small/penguin_lter_small.csv replace setup_script "test setup"

sqlacodegen $SQLALCHEMY_DATABASE_URI --outfile test_app_deploy_data/models.py --noinflect



