# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

"""
Pytest configuration and test fixtures
"""

from types import MappingProxyType

import pytest
from sqlalchemy.engine.url import URL

from database.local_handler import LocalCSVHandler
from graphics.plotly_plot import LAYOUT, TITLE
from utility.constants import *
from app_setup import configure_backend, create_app

TESTING_DB_CONFIG = {
    "drivername": "postgresql+psycopg2",
    "host": "localhost",
    "port": "5432",
    "username": "escalation",
    "password": "escalation_pwd",
    "database": "testing_escalation",
}
TESTING_DB_URI = URL(**TESTING_DB_CONFIG)


@pytest.fixture()
def test_app_client_csv_backed(main_json_csv_backend_fixture):

    flask_app = create_app()
    flask_app.config[APP_CONFIG_JSON] = MappingProxyType(main_json_csv_backend_fixture)
    flask_app.config[CONFIG_FILE_FOLDER] = TEST_APP_DEPLOY_DATA
    configure_backend(flask_app)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    # application context needs to be pushed to be able to handle GETs and POSTs
    ctx.push()
    # provide the testing client to the tests
    yield testing_client  # this is where the testing happens!
    # remove the context to clean up the test environment
    ctx.pop()


@pytest.fixture()
def test_app_client_sql_backed(main_json_sql_backend_fixture):
    flask_app = create_app(db_uri=TESTING_DB_URI)
    flask_app.config[APP_CONFIG_JSON] = MappingProxyType(main_json_sql_backend_fixture)
    flask_app.config[CONFIG_FILE_FOLDER] = TEST_APP_DEPLOY_DATA
    configure_backend(flask_app, models_path="test_app_deploy_data.models")
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    # application context needs to be pushed to be able to handle GETs and POSTs
    ctx.push()
    # provide the testing client to the tests
    yield testing_client  # this is where the testing happens!
    # remove the context to clean up the test environment
    ctx.pop()


@pytest.fixture()
def local_handler_fixture_small(test_app_client_csv_backed):
    got_data = LocalCSVHandler(
        {MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size_small"}}
    )
    return got_data


@pytest.fixture()
def local_handler_fixture(test_app_client_csv_backed):
    got_data = LocalCSVHandler({MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "penguin_size"}})
    return got_data


@pytest.fixture()
def main_json_csv_backend_fixture():
    return make_main_config_for_testing(backend=LOCAL_CSV)


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
                    }
                ]
            },
            VISUALIZATION_OPTIONS: {
                HOVER_DATA: {
                    COLUMN_NAME: ["penguin_size:sex", "penguin_size:culmen_length_mm",],
                },
                GROUPBY: {COLUMN_NAME: ["penguin_size:island", "penguin_size:sex",],},
            },
            SELECTABLE_DATA_DICT: {
                FILTER: [
                    {COLUMN_NAME: "penguin_size:sex", MULTIPLE: False,},
                    {COLUMN_NAME: "penguin_size:island", MULTIPLE: True,},
                ],
                NUMERICAL_FILTER: [{COLUMN_NAME: "penguin_size:culmen_length_mm",}],
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
                AXIS: [
                    {
                        OPTION_TYPE: "axis",
                        COLUMN_NAME: "x",
                        ENTRIES: [
                            "penguin_size:culmen_length_mm",
                            "penguin_size:flipper_length_mm",
                            "penguin_size:body_mass_g",
                            "penguin_size:culmen_depth_mm",
                        ],
                    }
                ],
                GROUPBY: {
                    ENTRIES: ["penguin_size:sex", "penguin_size:island"],
                    MULTIPLE: True,
                },
            },
        },
    }
    return pages
