# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import json
import os

from app_setup import create_app, configure_app
from utility.constants import APP_DEPLOY_DATA

if os.environ.get("CONFIG_FILE_PATH"):
    config_file_path = os.environ["CONFIG_FILE_PATH"]
else:
    config_file_path = os.path.join("app_deploy_data", "main_config.json")

if os.environ.get("APP_DEPLOY_DATA"):
    app_deploy_data = os.environ["APP_DEPLOY_DATA"]
else:
    app_deploy_data = APP_DEPLOY_DATA


config_file_path = os.path.join("app_deploy_data", "main_config.json")
# config_file_path = "test_app_deploy_data/test_sql_app_config.json"
# config_file_path = "test_app_deploy_data/test_app_local_config.json"

with open(config_file_path, "r") as config_file:
    config_dict = json.load(config_file)
app = create_app()
app = configure_app(
    app=app, config_dict=config_dict, config_file_folder=app_deploy_data
)

if __name__ == "__main__":
    app.run()
