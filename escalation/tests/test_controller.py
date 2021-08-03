# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy
import json

from tests.conftest import PEARL_HARBOR
from controller import (
    create_labels_for_available_pages,
    get_datasource_metadata_formatted_for_admin_panel,
)


def test_extract_buttons(main_json_sql_backend_fixture):
    aval_pg = main_json_sql_backend_fixture["available_pages"]
    buttons = create_labels_for_available_pages(aval_pg)

    button1 = {"webpage_label": "PENGUINS!", "link": "penguin"}
    assert button1 in buttons


def test_create_labels_for_available_pages():
    available_pages_list = [
        {
            "webpage_label": "PENGUINS!",
            "url_endpoint": "penguin",
            "graphic_config_files": ["big_penguins.json", "hist_penguins.json"],
        },
        {
            "webpage_label": "Radio Penguins",
            "url_endpoint": "radio_penguins",
            "graphic_config_files": ["radio_penguins.json"],
        },
    ]
    labels = create_labels_for_available_pages(available_pages_list)
    expected_labels = [
        {"webpage_label": "PENGUINS!", "link": "penguin"},
        {"webpage_label": "Radio Penguins", "link": "radio_penguins"},
    ]

    assert labels == expected_labels


def test_get_datasource_metadata_formatted_for_admin_panel(
    rebuild_test_database, test_app_client_sql_backed
):
    data_source_dict = get_datasource_metadata_formatted_for_admin_panel()
    pearl_harbor_timestring = PEARL_HARBOR.strftime("%Y-%m-%d %H:%M:%S")

    # 1 entry in upload metadata
    assert data_source_dict["penguin_size_small"] == {
        "ids": [1],
        "data": json.dumps(
            [
                {
                    "upload_id": 1,
                    "username": "test_fixture",
                    "upload_time": pearl_harbor_timestring,
                    "active": True,
                    "notes": "test case upload",
                }
            ]
        ),
    }

    # 2 entries in upload metadata
    assert data_source_dict["penguin_size"] == {
        "ids": [1, 2],
        "data": json.dumps(
            [
                {
                    "upload_id": 1,
                    "username": "test_fixture",
                    "upload_time": pearl_harbor_timestring,
                    "active": True,
                    "notes": "test case upload",
                },
                {
                    "upload_id": 2,
                    "username": "test_fixture",
                    "upload_time": pearl_harbor_timestring,
                    "active": True,
                    "notes": "test case upload",
                },
            ]
        ),
    }
