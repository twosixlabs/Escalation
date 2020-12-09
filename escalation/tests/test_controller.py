# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import json

from tests.conftest import PEARL_HARBOR
from controller import (
    create_labels_for_available_pages,
    create_data_subselect_info_for_plot,
    get_unique_set_of_columns_needed,
    make_filter_dict,
    get_datasource_metadata_formatted_for_admin_panel,
)
from graphics.plotly_plot import PlotlyPlot
from utility.constants import (
    JINJA_SELECT_HTML_FILE,
    ENTRIES,
    ACTIVE_SELECTORS,
    SHOW_ALL_ROW,
    SELECTABLE_DATA_DICT,
    TEXT,
    FILTER,
    NUMERICAL_FILTER,
    AXIS,
    MULTIPLE,
    DATA,
    MAX,
    VALUE,
    MIN,
    GROUPBY,
    NO_GROUP_BY,
)


def test_extract_buttons(main_json_sql_backend_fixture):
    aval_pg = main_json_sql_backend_fixture["available_pages"]
    buttons = create_labels_for_available_pages(aval_pg)

    button1 = {"webpage_label": "PENGUINS!", "link": "penguin"}
    assert button1 in buttons


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
        ],
        AXIS: [
            {
                "column": "x",
                "entries": [
                    "penguin_size:culmen_length_mm",
                    "penguin_size:flipper_length_mm",
                    "penguin_size:body_mass_g",
                ],
                ACTIVE_SELECTORS: ["penguin_size:culmen_length_mm"],
            }
        ],
    }
    graphic_json_fixture[SELECTABLE_DATA_DICT] = select_dict
    select_info = create_data_subselect_info_for_plot(
        graphic_json_fixture, sql_handler_fixture
    )

    assert select_info[0][JINJA_SELECT_HTML_FILE] == "selector.html"
    assert select_info[2][JINJA_SELECT_HTML_FILE] == "selector.html"

    assert "MALE" in select_info[1][ACTIVE_SELECTORS]
    assert "MALE" in select_info[1][ENTRIES]
    assert "FEMALE" in select_info[1][ENTRIES]
    assert "." in select_info[1][ENTRIES]  # yes this is a unique entry in the data set
    assert SHOW_ALL_ROW in select_info[2][ACTIVE_SELECTORS]
    assert "Biscoe" in select_info[2][ENTRIES]
    assert select_info[2][MULTIPLE]
    assert not select_info[1][MULTIPLE]
    assert "penguin_size:culmen_length_mm" in select_info[0][ENTRIES]
    assert "penguin_size:flipper_length_mm" in select_info[0][ENTRIES]
    assert "penguin_size:body_mass_g" in select_info[0][ENTRIES]
    assert "penguin_size:culmen_length_mm" in select_info[0][ACTIVE_SELECTORS]


def test_get_unique_set_of_columns_needed():
    culmen = "penguin_size:culmen_length_mm"
    flipper = "penguin_size:flipper_length_mm"
    flipper2 = "penguin_size:flipper_length_mm2"
    island = "penguin_size:island"
    sex = "penguin_size:sex"
    ploty_test = PlotlyPlot()
    test_cols_list = get_unique_set_of_columns_needed(
        ploty_test.get_data_columns(
            {DATA: [{"x": culmen, "y": flipper}, {"x": culmen, "y": flipper2},]}
        ),
        {"hover_data": {"column": [sex, culmen]}, "groupby": {"column": [island]},},
    )
    assert culmen in test_cols_list
    assert flipper in test_cols_list
    assert flipper2 in test_cols_list
    assert island in test_cols_list
    assert sex in test_cols_list
    assert len(test_cols_list) == 5


def test_create_data_subselect_info_for_plot_with_defaults(
    sql_handler_fixture, graphic_json_fixture
):
    plot_specification = graphic_json_fixture["graphic_0"]
    # add_active_selectors_to_selectable_data_list adds default  SHOW_ALL_ROWS to selectors
    for selector in plot_specification[SELECTABLE_DATA_DICT][FILTER]:
        selector[ACTIVE_SELECTORS] = [SHOW_ALL_ROW]
    numerical_filter_example_dict = {MAX: {VALUE: "3"}, MIN: {VALUE: ""}}
    plot_specification[SELECTABLE_DATA_DICT][NUMERICAL_FILTER][0][
        ACTIVE_SELECTORS
    ] = numerical_filter_example_dict
    select_info = create_data_subselect_info_for_plot(
        plot_specification, sql_handler_fixture
    )
    expected_select_info = [
        {
            "select_html_file": "selector.html",
            "type": "filter",
            "name": "filter_0",
            "active_selector": [SHOW_ALL_ROW],
            "entries": [SHOW_ALL_ROW, ".", "FEMALE", "MALE"],
            "multiple": False,
            TEXT: "Filter by penguin_size:sex",
        },
        {
            "select_html_file": "selector.html",
            "type": "filter",
            "name": "filter_1",
            "active_selector": [SHOW_ALL_ROW],
            "entries": [SHOW_ALL_ROW, "Biscoe", "Dream", "Torgersen"],
            "multiple": True,
            TEXT: "Filter by penguin_size:island",
        },
        {
            "select_html_file": "numerical_filter.html",
            "type": "numerical_filter",
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


def test_get_data_for_page():
    assert False


def test_assemble_html_with_graphs_from_page_config():
    assert False


def test_assemble_plot_from_instructions():
    assert False


def test_create_labels_for_available_pages():
    assert False


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
        "type": "filter",
        "select_html_file": "selector.html",
        "name": "filter_0",
        "text": "Filter by penguin_size:sex",
        "active_selector": ["Show All Rows"],
        "multiple": False,
        "entries": penguin_sexes,
    }
    assert created_filter_dicts[0] == expected_filter_dict_sexes

    expected_filter_dict_islands = {
        "type": "filter",
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
        "type": "numerical_filter",
        "select_html_file": "numerical_filter.html",
        "name": "numerical_filter_0",
        "text": "Filter by penguin_size:culmen_length_mm",
        "active_selector": {"max": {"value": ""}, "min": {"value": ""}},
        "multiple": False,
        "entries": None,
    }
    assert expected_numerical_filter_dict == created_filter_dict


def test_make_filter_dict_axis_groupby():
    axis_entries = [
        "penguin_size:body_mass_g",
        "penguin_size:culmen_depth_mm",
        "penguin_size:culmen_length_mm",
        "penguin_size:flipper_length_mm",
    ]
    groupby_entries = [NO_GROUP_BY, "penguin_size:sex", "penguin_size:island"]
    selector_dict = {
        "axis": [
            {
                "column": "x",
                "entries": axis_entries,
                "active_selector": "penguin_size:body_mass_g",
            }
        ],
        "groupby": {
            "entries": groupby_entries,
            "multiple": True,
            "active_selector": ["penguin_size:island"],
        },
    }

    created_axis_dict = make_filter_dict(
        AXIS,
        selector_dict[AXIS][0],  # get the entry from the list of axes
        index=0,
        selector_entries=axis_entries,
    )
    expected_axis_dict = {
        "type": "axis",
        "select_html_file": "selector.html",
        "name": "axis_0",
        "text": "x axis",
        "active_selector": "penguin_size:body_mass_g",
        "multiple": False,
        "entries": axis_entries,
    }
    assert created_axis_dict == expected_axis_dict

    created_groupby_dict = make_filter_dict(
        GROUPBY,
        selector_dict[GROUPBY],  # get the entry from the list of filters
        index=0,
        selector_entries=groupby_entries,
    )
    expected_groupby_dict = {
        "type": "groupby",
        "select_html_file": "selector.html",
        "name": "groupby",
        "text": "Group by:",
        "active_selector": ["penguin_size:island"],
        "multiple": True,
        "entries": groupby_entries,
    }
    assert created_groupby_dict == expected_groupby_dict


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
