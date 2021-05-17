# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

"""
Pytest configuration and test fixtures
"""
from datetime import datetime
import os
from types import MappingProxyType

import pandas as pd
import pytest
from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from werkzeug.datastructures import FileStorage

from database.sql_handler import SqlDataInventory, SqlHandler
from graphics.plotly_plot import LAYOUT, TITLE
from tests.test_file_uploads import TEST_FILENAME
from utility.constants import *
from app_setup import configure_backend, create_app
from utility.constants import (
    TEST_APP_DEPLOY_DATA,
    DATA,
    DATA_UPLOAD_METADATA,
    MAIN_DATA_SOURCE,
    DATA_SOURCE_TYPE,
    ADDITIONAL_DATA_SOURCES,
    JOIN_KEYS,
)

TESTING_DB_CONFIG = {
    "drivername": "postgresql+psycopg2",
    "host": "localhost",
    "port": "5432",
    "username": "escalation",
    "password": "escalation_pwd",
    "database": "testing_escalation",
}
TESTING_DB_URI = URL(**TESTING_DB_CONFIG)

# define a fixed time for test uploads
PEARL_HARBOR = datetime(1941, 12, 7, 7, 55, 0)


@pytest.fixture()
def addendum_dict():
    addendum_dict = {
        "graphic_0": {
            "filter_0": ["MALE"],
            "filter_1": ["Torgersen", "Dream"],
            "numerical_filter_0_max_value": ["4"],
            "numerical_filter_0_min_value": [""],
        }
    }
    return addendum_dict


@pytest.fixture()
def rebuild_test_database(test_app_client_sql_backed, mocker):
    # drop all tables associated with the testing app Sqlalchemy Base
    engine = create_engine(TESTING_DB_URI)
    current_app.engine = engine
    current_app.Base.metadata.drop_all(bind=engine)
    current_app.Base.metadata.create_all(bind=engine)

    test_app_data_path = os.path.join(TEST_APP_DEPLOY_DATA, DATA)
    data_sources = os.listdir(test_app_data_path)
    for data_source in data_sources:
        if data_source == DATA_UPLOAD_METADATA or data_source.startswith("."):
            continue
        data_inventory = SqlDataInventory(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source}}
        )
        data_inventory.get_upload_time = mocker.MagicMock(return_value=PEARL_HARBOR)
        data_source_path = os.path.join(test_app_data_path, data_source)
        files = os.listdir(data_source_path)
        for file in files:
            df = pd.read_csv(os.path.join(data_source_path, file), sep=",", comment="#")
            data_inventory.write_data_upload_to_backend(
                df, username="test_fixture", notes="test case upload"
            )
    return True


@pytest.fixture()
def test_app_client_sql_backed(main_json_sql_backend_fixture):
    # set an env other than DEVELOPMENT, which is used as a gate for some features
    flask_app = create_app(db_uri=TESTING_DB_URI, env="testing")
    flask_app.config[APP_CONFIG_JSON] = MappingProxyType(main_json_sql_backend_fixture)
    flask_app.config[CONFIG_FILE_FOLDER] = TEST_APP_DEPLOY_DATA
    configure_backend(flask_app)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    # application context needs to be pushed to be able to handle GETs and POSTs
    ctx.push()
    # provide the testing client to the tests
    yield testing_client  # this is where the testing happens!
    # remove the context to clean up the test environment
    ctx.pop()


@pytest.fixture()
def test_app_client_sql_backed_development_env(main_json_sql_backend_fixture):
    flask_app = create_app(db_uri=TESTING_DB_URI, env=DEVELOPMENT)
    flask_app.config[APP_CONFIG_JSON] = MappingProxyType(main_json_sql_backend_fixture)
    flask_app.config[CONFIG_FILE_FOLDER] = TEST_APP_DEPLOY_DATA
    configure_backend(flask_app)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    # application context needs to be pushed to be able to handle GETs and POSTs
    ctx.push()
    # provide the testing client to the tests
    yield testing_client  # this is where the testing happens!
    # remove the context to clean up the test environment
    ctx.pop()


@pytest.fixture()
def main_json_sql_backend_fixture():
    return make_main_config_for_testing(backend=POSTGRES)


@pytest.fixture()
def graphic_json_fixture():
    return make_graphic_config_for_testing()


def make_main_config_for_testing(backend):
    config_dict = {
        SITE_TITLE: "Escalation Test",
        "brief_desc": "This is a test/demo for the Escalation OS",
        DATA_BACKEND: backend,
        AVAILABLE_PAGES: [
            {
                WEBPAGE_LABEL: "PENGUINS!",
                URL_ENDPOINT: "penguin",
                GRAPHIC_CONFIG_FILES: ["big_penguins.json", "hist_penguins.json"],
            },
            {
                WEBPAGE_LABEL: "Radio Penguins",
                URL_ENDPOINT: "radio_penguins",
                GRAPHIC_CONFIG_FILES: ["radio_penguins.json"],
            },
        ],
    }
    return config_dict


def make_graphic_config_for_testing():
    pages = {
        "graphic_0": {
            PLOT_MANAGER: "plotly",
            DATA_SOURCES: {MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size"}},
            GRAPHIC_TITLE: "Do massive penguins have long flippers?",
            GRAPHIC_DESC: "This plot looks at the relationship between...",
            PLOT_SPECIFIC_INFO: {
                DATA: [
                    {
                        "type": "scatter",
                        "x": "penguin_size:body_mass_g",
                        "y": "penguin_size:flipper_length_mm",
                        HOVERTEXT: [
                            "penguin_size:sex",
                            "penguin_size:culmen_length_mm",
                        ],
                        TRANSFORMS: {
                            GROUPBY: {
                                GROUPS: ["penguin_size:island", "penguin_size:sex",],
                            }
                        },
                    }
                ]
            },
            SELECTABLE_DATA_DICT: {
                FILTER: [
                    {COLUMN_NAME: "penguin_size:sex", MULTIPLE: False,},
                    {COLUMN_NAME: "penguin_size:island", MULTIPLE: True,},
                ],
                NUMERICAL_FILTER: [
                    {COLUMN_NAME: "penguin_size:culmen_length_mm", TYPE: "number"}
                ],
            },
        },
        "graphic_1": {
            PLOT_MANAGER: "plotly",
            DATA_SOURCES: {MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size"}},
            GRAPHIC_TITLE: "How big are penguins?",
            GRAPHIC_DESC: ".",
            PLOT_SPECIFIC_INFO: {
                DATA: [{"type": "histogram", "x": "penguin_size:body_mass_g"}],
                LAYOUT: {
                    AXIS.format("x"): {TITLE, "body mass"},
                    AXIS.format("y"): {TITLE, "count"},
                },
            },
            SELECTABLE_DATA_DICT: {
                GROUPBY: {
                    ENTRIES: ["penguin_size:sex", "penguin_size:island"],
                    MULTIPLE: True,
                    DEFAULT_SELECTED: ["penguin_size:sex"],
                },
            },
        },
    }
    return pages


@pytest.fixture()
def sql_handler_fixture(rebuild_test_database):
    data_sources = {
        MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size"},
        ADDITIONAL_DATA_SOURCES: [
            {
                DATA_SOURCE_TYPE: "mean_penguin_stat",
                JOIN_KEYS: [
                    ["penguin_size:study_name", "mean_penguin_stat:study_name"],
                    ["penguin_size:sex", "mean_penguin_stat:sex"],
                    ["penguin_size:species", "mean_penguin_stat:species"],
                ],
            }
        ],
    }
    return SqlHandler(data_sources)


@pytest.fixture()
def sql_data_inventory_fixture(rebuild_test_database):
    data_sources = {
        MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size"},
    }
    return SqlDataInventory(data_sources)


@pytest.fixture
def penguin_size_csv_file():
    request_file = FileStorage(
        stream=open(TEST_FILENAME, "rb"), filename=TEST_FILENAME,
    )
    return request_file
