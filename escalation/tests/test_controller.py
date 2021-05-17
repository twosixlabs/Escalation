# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy
import json

from tests.conftest import PEARL_HARBOR
from controller import (
    create_labels_for_available_pages,
    get_datasource_metadata_formatted_for_admin_panel,
    make_dict_of_graphic_objects,
)
from tests.conftest import graphic_json_fixture, addendum_dict
from utility.constants import (
    ACTIVE_SELECTORS,
    SHOW_ALL_ROW,
    SELECTABLE_DATA_DICT,
    FILTER,
    GRAPHIC_NUM,
    DATA_FILTERS,
)


def test_make_dict_of_graphic_classes(graphic_json_fixture, addendum_dict):
    single_page_config_dict = graphic_json_fixture
    single_page_config_dict_test = copy.deepcopy(single_page_config_dict)
    graphic_class_dict = make_dict_of_graphic_objects(
        single_page_config_dict_test, None
    )
    # add instructions should call the other two methods which I am already testing for.
    # So I want to make sure it in actually doing something
    assert (
        graphic_class_dict[GRAPHIC_NUM.format(0)].graphic_dict
        != single_page_config_dict[GRAPHIC_NUM.format(0)]
    )
    assert DATA_FILTERS not in graphic_class_dict[GRAPHIC_NUM.format(0)].graphic_dict

    single_page_config_dict_test = copy.deepcopy(single_page_config_dict)
    graphic_class_dict = make_dict_of_graphic_objects(
        single_page_config_dict_test, addendum_dict
    )
    assert DATA_FILTERS in graphic_class_dict[GRAPHIC_NUM.format(0)].graphic_dict


def test_make_dict_of_graphic_classes_with_different_addendum(
    graphic_json_fixture, addendum_dict
):
    single_page_config_dict = graphic_json_fixture
    single_page_config_dict_test = copy.deepcopy(single_page_config_dict)
    new_addendum_dict = {"a_different_graph": addendum_dict[GRAPHIC_NUM.format(0)]}
    graphic_class_dict = make_dict_of_graphic_objects(
        single_page_config_dict_test, new_addendum_dict
    )
    graphic_0_dict = graphic_class_dict[GRAPHIC_NUM.format(0)].graphic_dict
    assert len(graphic_0_dict[SELECTABLE_DATA_DICT][FILTER][0][ACTIVE_SELECTORS]) == 1
    assert (
        SHOW_ALL_ROW
        in graphic_0_dict[SELECTABLE_DATA_DICT][FILTER][0][ACTIVE_SELECTORS]
    )


def test_extract_buttons(main_json_sql_backend_fixture):
    aval_pg = main_json_sql_backend_fixture["available_pages"]
    buttons = create_labels_for_available_pages(aval_pg)

    button1 = {"webpage_label": "PENGUINS!", "link": "penguin"}
    assert button1 in buttons


def test_get_data_for_page():
    assert False


def test_assemble_html_with_graphs_from_page_config():
    assert False


def test_assemble_plot_from_instructions():
    assert False


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


def test_make_pages_dict():
    assert False


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
