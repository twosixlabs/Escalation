# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import copy

import pytest
from werkzeug.datastructures import ImmutableMultiDict

from graphics.graphic_class import get_key_for_form, make_filter_dict
from graphics.plotly_plot import PlotlyPlot
from tests.conftest import graphic_json_fixture, addendum_dict
from utility.constants import (
    AVAILABLE_PAGES,
    DATA,
    GRAPHIC_NUM,
    GRAPHICS,
    SELECTABLE_DATA_DICT,
    SHOW_ALL_ROW,
    UPPER_INEQUALITY,
    VALUE,
    OPERATION,
    ACTIVE_SELECTORS,
    DATA_FILTERS,
    FILTER,
    NUMERICAL_FILTER,
    GROUPBY,
    COLUMN_NAME,
    PLOT_SPECIFIC_INFO,
    DEFAULT_SELECTED,
    MAX,
    MIN,
    TRANSFORMS,
    GROUPS,
    NO_GROUP_BY,
    TEXT,
    JINJA_SELECT_HTML_FILE,
    ENTRIES,
    MULTIPLE,
    FILTERED_SELECTOR,
)


def test_add_active_selectors_to_selectable_data_list_with_addendum(
    graphic_json_fixture, addendum_dict
):
    graphic_0_dict = graphic_json_fixture["graphic_0"]
    graphic_class = PlotlyPlot(graphic_0_dict, addendum_dict["graphic_0"],)
    graphic_class.add_active_selectors_to_selectable_data_list()
    filter_list = graphic_class.graphic_dict[SELECTABLE_DATA_DICT][FILTER]
    assert len(filter_list[0][ACTIVE_SELECTORS]) == 1
    assert "MALE" in filter_list[0][ACTIVE_SELECTORS]
    assert len(filter_list[1][ACTIVE_SELECTORS]) == 2
    assert "Torgersen" in filter_list[1][ACTIVE_SELECTORS]
    assert "Dream" in filter_list[1][ACTIVE_SELECTORS]

    numerical_filter_list = graphic_class.graphic_dict[SELECTABLE_DATA_DICT][
        NUMERICAL_FILTER
    ]
    assert numerical_filter_list[0][ACTIVE_SELECTORS][MAX][VALUE] == "4"
    assert numerical_filter_list[0][ACTIVE_SELECTORS][MIN][VALUE] == ""


def test_add_active_selectors_to_selectable_data_list_with_SHOW_ALL_ROWS_chosen(
    graphic_json_fixture,
):
    addendum_dict = {
        "filter_0": ["MALE"],
        "filter_1": [SHOW_ALL_ROW],
        "numerical_filter_0_max_value": ["4"],
        "numerical_filter_0_min_value": [""],
    }
    graphic_0_dict = graphic_json_fixture["graphic_0"]
    graphic_class = PlotlyPlot(graphic_0_dict, addendum_dict,)
    graphic_class.add_active_selectors_to_selectable_data_list()
    graphic_dict = graphic_class.graphic_dict
    assert len(graphic_dict[SELECTABLE_DATA_DICT][FILTER][1][ACTIVE_SELECTORS]) == 1
    assert (
        SHOW_ALL_ROW in graphic_dict[SELECTABLE_DATA_DICT][FILTER][1][ACTIVE_SELECTORS]
    )


def test_add_active_selectors_to_selectable_data_list_without_addendum(
    graphic_json_fixture,
):
    graphic_0_dict = graphic_json_fixture["graphic_0"]
    graphic_0_dict[SELECTABLE_DATA_DICT][FILTER][1][DEFAULT_SELECTED] = ["Dream"]

    graphic_class = PlotlyPlot(graphic_0_dict,)
    graphic_class.add_active_selectors_to_selectable_data_list()

    filter_list = graphic_class.graphic_dict[SELECTABLE_DATA_DICT][FILTER]
    assert len(filter_list[0][ACTIVE_SELECTORS]) == 1
    assert SHOW_ALL_ROW in filter_list[0][ACTIVE_SELECTORS]
    assert len(filter_list[1][ACTIVE_SELECTORS]) == 1
    assert "Dream" in filter_list[1][ACTIVE_SELECTORS]

    numerical_filter_list = graphic_class.graphic_dict[SELECTABLE_DATA_DICT][
        NUMERICAL_FILTER
    ]
    assert numerical_filter_list[0][ACTIVE_SELECTORS][MAX][VALUE] == ""
    assert numerical_filter_list[0][ACTIVE_SELECTORS][MIN][VALUE] == ""

    graphic_1_dict = graphic_json_fixture["graphic_1"]
    graphic_class = PlotlyPlot(graphic_1_dict,)
    graphic_class.add_active_selectors_to_selectable_data_list()
    groupby_list = graphic_class.graphic_dict[SELECTABLE_DATA_DICT][GROUPBY]
    assert groupby_list[ACTIVE_SELECTORS] == ["penguin_size:sex"]


def test_add_operations_to_the_data(graphic_json_fixture, addendum_dict):
    graphic_json_fixture = graphic_json_fixture
    graphic_0_dict = graphic_json_fixture["graphic_0"]
    graphic_class = PlotlyPlot(graphic_0_dict, addendum_dict["graphic_0"],)
    graphic_class.add_operations_to_the_data_from_addendum()
    operations_list = graphic_class.graphic_dict[DATA_FILTERS]
    assert len(operations_list) == 3

    assert operations_list[0] == {
        "type": "filter",
        "column": "penguin_size:sex",
        "selected": ["MALE"],
        FILTERED_SELECTOR: False,
    }
    assert operations_list[1] == {
        "type": "filter",
        "column": "penguin_size:island",
        "selected": ["Torgersen", "Dream"],
        FILTERED_SELECTOR: False,
    }
    assert operations_list[2] == {
        "type": "numerical_filter",
        "column": "penguin_size:culmen_length_mm",
        "operation": "<=",
        "value": 4.0,
    }


def test_add_operations_to_the_data_from_defaults(graphic_json_fixture):
    selectable_data_dict = graphic_json_fixture["graphic_0"][SELECTABLE_DATA_DICT]
    selectable_data_dict[NUMERICAL_FILTER][0][MIN] = 2

    graphic_class = PlotlyPlot(graphic_json_fixture["graphic_0"])
    graphic_class.add_operations_to_the_data_from_defaults()
    operations_list = graphic_class.graphic_dict[DATA_FILTERS]
    assert len(operations_list) == 1

    assert operations_list[0] == {
        "type": "numerical_filter",
        "column": "penguin_size:culmen_length_mm",
        "operation": ">=",
        "value": 2.0,
    }


def test_modify_config_based_on_json(graphic_json_fixture):
    graphic_1_dict = graphic_json_fixture["graphic_1"]
    addendum_dict = {
        GROUPBY: ["penguin_size:island"],
    }
    assert TRANSFORMS not in graphic_1_dict[PLOT_SPECIFIC_INFO][DATA][0]

    graphic_class = PlotlyPlot(graphic_1_dict, addendum_dict,)
    graphic_class.modify_graphic_dict_based_on_addendum_dict()

    assert graphic_class.graphic_dict[PLOT_SPECIFIC_INFO][DATA][0][TRANSFORMS][GROUPBY][
        GROUPS
    ] == ["penguin_size:island"]

    # test defualt selected
    graphic_class = PlotlyPlot(graphic_1_dict,)
    graphic_class.modify_graphic_dict_based_on_addendum_dict()

    assert graphic_class.graphic_dict[PLOT_SPECIFIC_INFO][DATA][0][TRANSFORMS][GROUPBY][
        GROUPS
    ] == ["penguin_size:sex"]


def test_get_key_for_form():
    assert "filter_1" == get_key_for_form(FILTER, 1)
    assert "numerical_filter_4" == get_key_for_form(NUMERICAL_FILTER, 4)
    assert "groupby" == get_key_for_form(GROUPBY, "")


def test_make_filter_dict_filters():
    selector_dict = {
        "filter": [
            {
                "column": "penguin_size:sex",
                "multiple": False,
                "active_selector": ["Show All Rows"],
            },
            {
                "column": "penguin_size:island",
                "multiple": True,
                "default_selected": ["Dream"],
                "active_selector": ["Dream"],
            },
        ],
        "numerical_filter": [
            {
                "column": "penguin_size:culmen_length_mm",
                "type": "number",
                "active_selector": {"max": {"value": ""}, "min": {"value": ""}},
            }
        ],
    }

    penguin_sexes = ([SHOW_ALL_ROW, "XX", "XY"],)  # penguin sexes column entries
    penguin_islands = [SHOW_ALL_ROW, "Dream"]  # penguin islands column entries

    entries_for_columns = [penguin_sexes, penguin_islands]
    created_filter_dicts = []
    for index, selector_items in enumerate(selector_dict[FILTER]):
        created_filter_dicts.append(
            make_filter_dict(
                FILTER,
                selector_items,
                index,
                selector_entries=entries_for_columns[index],
            )
        )

    expected_filter_dict_sexes = {
        "type": "",
        "select_html_file": "selector.html",
        "name": "filter_0",
        "text": "Filter by penguin_size:sex",
        "active_selector": ["Show All Rows"],
        "multiple": False,
        "entries": penguin_sexes,
    }
    assert created_filter_dicts[0] == expected_filter_dict_sexes

    expected_filter_dict_islands = {
        "type": "",
        "select_html_file": "selector.html",
        "name": "filter_1",
        "text": "Filter by penguin_size:island",
        "active_selector": ["Dream"],
        "multiple": True,
        "entries": penguin_islands,
    }
    assert created_filter_dicts[1] == expected_filter_dict_islands

    created_filter_dict = make_filter_dict(
        NUMERICAL_FILTER,
        selector_dict[NUMERICAL_FILTER][0],  # get the entry from the list of filters
        index=0,
    )

    expected_numerical_filter_dict = {
        "type": "number",
        "select_html_file": "numerical_filter.html",
        "name": "numerical_filter_0",
        "text": "Filter by penguin_size:culmen_length_mm",
        "active_selector": {"max": {"value": ""}, "min": {"value": ""}},
        "multiple": False,
        "entries": None,
    }
    assert expected_numerical_filter_dict == created_filter_dict


def test_make_filter_dict_groupby():
    groupby_entries = [NO_GROUP_BY, "penguin_size:sex", "penguin_size:island"]
    selector_dict = {
        "groupby": {
            "entries": groupby_entries,
            "multiple": True,
            "active_selector": ["penguin_size:island"],
        },
    }

    created_groupby_dict = make_filter_dict(
        GROUPBY,
        selector_dict[GROUPBY],  # get the entry from the list of filters
        index=0,
        selector_entries=groupby_entries,
    )
    expected_groupby_dict = {
        "type": "",
        "select_html_file": "selector.html",
        "name": "groupby",
        "text": "Group by:",
        "active_selector": ["penguin_size:island"],
        "multiple": True,
        "entries": groupby_entries,
    }
    assert created_groupby_dict == expected_groupby_dict


def test_create_data_subselect_info(sql_handler_fixture, graphic_json_fixture):
    select_dict = {
        FILTER: [
            {
                "column": "penguin_size:sex",
                "multiple": False,
                ACTIVE_SELECTORS: ["MALE"],
            },
            {
                "column": "penguin_size:island",
                "multiple": True,
                ACTIVE_SELECTORS: [SHOW_ALL_ROW],
            },
        ]
    }
    graphic_0_dict = graphic_json_fixture["graphic_0"]
    graphic_0_dict[SELECTABLE_DATA_DICT] = select_dict
    graphic_class = PlotlyPlot(graphic_0_dict,)
    data_filters = graphic_class.graphic_dict.get(DATA_FILTERS, [])
    unique_entry_dict = sql_handler_fixture.get_column_unique_entries(
        graphic_class.get_columns_that_need_unique_entries(), filters=data_filters
    )
    graphic_class.unique_entry_dict = unique_entry_dict
    graphic_class.create_data_subselect_info_for_plot()
    select_info = graphic_class.select_info

    assert select_info[1][JINJA_SELECT_HTML_FILE] == "selector.html"

    assert "MALE" in select_info[0][ACTIVE_SELECTORS]
    assert "MALE" in select_info[0][ENTRIES]
    assert "FEMALE" in select_info[0][ENTRIES]
    assert "." in select_info[0][ENTRIES]  # yes this is a unique entry in the data set
    assert SHOW_ALL_ROW in select_info[1][ACTIVE_SELECTORS]
    assert "Biscoe" in select_info[1][ENTRIES]
    assert select_info[1][MULTIPLE]
    assert not select_info[0][MULTIPLE]


def test_create_data_subselect_info_for_plot_with_defaults(
    sql_handler_fixture, graphic_json_fixture
):
    graphic_0_dict = graphic_json_fixture["graphic_0"]
    # add_active_selectors_to_selectable_data_list adds default  SHOW_ALL_ROWS to selectors
    for selector in graphic_0_dict[SELECTABLE_DATA_DICT][FILTER]:
        selector[ACTIVE_SELECTORS] = [SHOW_ALL_ROW]
    numerical_filter_example_dict = {MAX: {VALUE: "3"}, MIN: {VALUE: ""}}
    graphic_0_dict[SELECTABLE_DATA_DICT][NUMERICAL_FILTER][0][
        ACTIVE_SELECTORS
    ] = numerical_filter_example_dict

    graphic_class = PlotlyPlot(graphic_0_dict,)
    data_filters = graphic_class.graphic_dict.get(DATA_FILTERS, [])
    unique_entry_dict = sql_handler_fixture.get_column_unique_entries(
        graphic_class.get_columns_that_need_unique_entries(), filters=data_filters
    )
    graphic_class.unique_entry_dict = unique_entry_dict
    graphic_class.create_data_subselect_info_for_plot()
    select_info = graphic_class.select_info
    expected_select_info = [
        {
            "select_html_file": "selector.html",
            "type": "",
            "name": "filter_0",
            "active_selector": [SHOW_ALL_ROW],
            "entries": [SHOW_ALL_ROW, ".", "FEMALE", "MALE"],
            "multiple": False,
            TEXT: "Filter by penguin_size:sex",
        },
        {
            "select_html_file": "selector.html",
            "type": "",
            "name": "filter_1",
            "active_selector": [SHOW_ALL_ROW],
            "entries": [SHOW_ALL_ROW, "Biscoe", "Dream", "Torgersen"],
            "multiple": True,
            TEXT: "Filter by penguin_size:island",
        },
        {
            "select_html_file": "numerical_filter.html",
            "type": "number",
            "name": "numerical_filter_0",
            "active_selector": numerical_filter_example_dict,
            "entries": None,
            "multiple": False,
            TEXT: "Filter by penguin_size:culmen_length_mm",
        },
    ]
    assert select_info[0] == expected_select_info[0]
    assert select_info[1] == expected_select_info[1]
    assert select_info[2] == expected_select_info[2]
