# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import json
import os
from collections import deque

from flask import Flask
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from sqlalchemy.engine.url import URL
from app_deploy_data.app_settings import DATABASE_CONFIG
from app_setup import configure_backend
from utility.build_schema import build_settings_schema, build_graphic_schema
from utility.constants import *


def create_validate_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL")
        or URL(**DATABASE_CONFIG),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        VERSION="0.0.1",
    )
    return app


def load_config_file(config_file_path):
    with open(config_file_path, "r") as config_file:
        return json.load(config_file)


def get_data_inventory_class(csv_flag):
    if csv_flag:
        from database.local_handler import LocalCSVDataInventory

        data_inventory_class = LocalCSVDataInventory
    else:
        from database.sql_handler import SqlDataInventory

        data_inventory_class = SqlDataInventory
    return data_inventory_class


def get_possible_column_names(data_source_names, data_inventory_class, csv_flag):
    possible_column_names = []
    for data_source_name in data_source_names:
        data_inventory = data_inventory_class(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source_name}}
        )
        column_names = data_inventory.get_schema_for_data_source()
        possible_column_names.extend(
            [
                TABLE_COLUMN_SEPARATOR.join(
                    [data_source_name, column_name if csv_flag else column_name.name,]
                )
                for column_name in column_names
            ]
        )
    return possible_column_names


def validate_config_data_references(config_dict_path):
    """
    Validates that
    1. config_dict is of form needed for Escalate OS
    2. all data source and column names references exist in the data
    :param config_dict:
    :return:
    """
    try:
        schema = build_settings_schema()
        current_config_path = config_dict_path
        config_dict = load_config_file(current_config_path)
        validate(instance=config_dict, schema=schema)
        app = create_validate_app()
        app.config[APP_CONFIG_JSON] = config_dict
        app.config[CONFIG_FILE_FOLDER] = TEST_APP_DEPLOY_DATA
        configure_backend(app)
        ctx = app.app_context()
        ctx.push()
        # handle code differently at two spots depending on whether we are dealing with file system or database
        csv_flag = config_dict[DATA_BACKEND] == LOCAL_CSV
        # data_backend_writer may be useful
        data_inventory_class = get_data_inventory_class(csv_flag)
        data_source_names_found = data_inventory_class.get_available_data_sources()

        possible_column_names = get_possible_column_names(
            data_source_names_found, data_inventory_class, csv_flag
        )
        # put column names in format "data_source_name.column_name"
        schema = build_graphic_schema(data_source_names_found, possible_column_names)

        pages = config_dict.get(AVAILABLE_PAGES, [])
        for page in pages:
            graphic_config_file_paths = page.get(GRAPHIC_CONFIG_FILES, [])
            for graphic_config_file_path in graphic_config_file_paths:
                current_config_path = os.path.join(
                    app.config[CONFIG_FILE_FOLDER], graphic_config_file_path
                )
                validate(instance=load_config_file(current_config_path), schema=schema)
        print("Your config file is valid")
    except ValidationError as valid_error:
        print("{} is not valid:".format(current_config_path))
        print(valid_error.message)
        print("The error can be found in the config at:", list(valid_error.path))


if __name__ == "__main__":
    # todo: take this in as a command line argument
    main_config_file_path = "test_app_deploy_data/test_app_local_config.json"
    validate_config_data_references(main_config_file_path)
