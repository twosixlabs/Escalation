import copy

from werkzeug.datastructures import ImmutableMultiDict

from utility.constants import (
    HOVER_DATA,
    COLUMN_NAME,
    GROUPBY,
    AGGREGATE,
    FILTER,
    NUMERICAL_FILTER,
    MULTIPLE,
    AXIS,
    GRAPHIC_META_INFO,
    VISUALIZATION,
    SELECTOR,
    PLOTLY,
    ADDITIONAL_DATA_SOURCES,
    DATA_SOURCE_TYPE,
    JOIN_KEYS,
    DATA_SOURCES,
    SITE_TITLE,
    SITE_DESC,
    DATA_BACKEND,
    POSTGRES,
    PLOT_SPECIFIC_INFO,
    SELECTABLE_DATA_DICT,
    VISUALIZATION_OPTIONS,
    GROUPBY_SELECTOR,
    MAX_ENTRIES_FOR_FILTER_SELECTOR,
)
from utility.wizard_utils import (
    invert_dict_lists,
    sanitize_string,
    prune_visualization_dict,
    prune_selector_dict,
    make_empty_component_dict,
    extract_data_sources_from_config,
    copy_data_from_form_to_config,
    graphic_dict_to_graphic_component_dict,
    graphic_component_dict_to_graphic_dict,
    generate_collapse_dict_from_graphic_component_dict,
    divide_columns_into_type_of_filters,
)

from sqlalchemy.types import Integer, Text, Float, DateTime, ARRAY, Boolean


def test_invert_dict_lists():
    test_dict = {"a": [1], "b": [2, 3]}
    expected_dict = {1: "a", 2: "b", 3: "b"}
    inverted_dict = invert_dict_lists(test_dict)
    assert inverted_dict == expected_dict


def test_get_layout_for_dashboard(main_json_sql_backend_fixture):
    # Need to set up file system
    # new_dict = get_layout_for_dashboard(main_json_csv_backend_fixture[AVAILABLE_PAGES])
    #
    # ground_truth = (
    #     [
    #         {
    #             WEBPAGE_LABEL: "PENGUINS!",
    #             URL_ENDPOINT: "penguin",
    #             GRAPHIC_CONFIG_FILES: [
    #                 {GRAPHIC_PATH: "big_penguins.json"},
    #                 "hist_penguins.json",
    #             ],
    #         },
    #         {
    #             WEBPAGE_LABEL: "Radio Penguins",
    #             URL_ENDPOINT: "radio_penguins",
    #             GRAPHIC_CONFIG_FILES: ["radio_penguins.json"],
    #         },
    #     ],
    # )
    assert False


def test_sanitize_string():
    test_string = r"this! i:/\s*$. test 42"
    sanitized = r"this_is_test_42"
    assert sanitize_string(test_string) == sanitized


def test_prune_visualization_dict():
    visualization_dict = {
        HOVER_DATA: {
            COLUMN_NAME: ["penguin_size:sex", "penguin_size:culmen_length_mm",],
        },
        GROUPBY: {COLUMN_NAME: ["penguin_size:island", "penguin_size:sex",],},
    }

    visualization_dict_copy = copy.deepcopy(visualization_dict)
    visualization_dict_copy[AGGREGATE] = {}
    assert prune_visualization_dict(visualization_dict_copy) == visualization_dict
    empty_dict = {
        HOVER_DATA: {COLUMN_NAME: [],},
        GROUPBY: {COLUMN_NAME: [],},
    }
    assert prune_visualization_dict(empty_dict) == {}


def test_prune_selector_dict():
    select_dict = {
        FILTER: [
            {COLUMN_NAME: "penguin_size:sex", MULTIPLE: False,},
            {COLUMN_NAME: "penguin_size:island", MULTIPLE: True,},
        ],
        NUMERICAL_FILTER: [{COLUMN_NAME: "penguin_size:culmen_length_mm",}],
    }
    select_dict_copy = copy.deepcopy(select_dict)
    select_dict_copy[AXIS] = []
    select_dict_copy[GROUPBY] = {}
    assert prune_selector_dict(select_dict_copy) == select_dict
    empty_dict = {
        FILTER: [],
        NUMERICAL_FILTER: [],
    }
    assert prune_selector_dict(empty_dict) == {}


def test_make_empty_component_dict():
    component_dict = make_empty_component_dict()
    assert component_dict[GRAPHIC_META_INFO] == {}
    assert component_dict[VISUALIZATION] == {}
    assert component_dict[SELECTOR] == {}
    assert component_dict[PLOTLY] == {}
    assert len(component_dict.keys()) == 4


def test_extract_data_sources_from_config(graphic_json_fixture):
    test_config = graphic_json_fixture["graphic_0"]
    test_config[DATA_SOURCES][ADDITIONAL_DATA_SOURCES] = [
        {
            DATA_SOURCE_TYPE: "mean_penguin_stat",
            JOIN_KEYS: [
                ["penguin_size:study_name", "mean_penguin_stat:study_name"],
                ["penguin_size:sex", "mean_penguin_stat:sex"],
                ["penguin_size:species", "mean_penguin_stat:species"],
            ],
        }
    ]
    data_sources = extract_data_sources_from_config(test_config)
    assert "penguin_size" in data_sources
    assert "mean_penguin_stat" in data_sources
    assert len(data_sources) == 2


def test_copy_data_from_form_to_config(main_json_sql_backend_fixture):
    main_config = copy.deepcopy(main_json_sql_backend_fixture)
    placer_holder_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod"
        " tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam"
    )
    test_title = "test_14"
    form = ImmutableMultiDict(
        [
            (SITE_TITLE, test_title),
            (SITE_DESC, placer_holder_text),
            (DATA_BACKEND, POSTGRES),
        ]
    )
    copy_data_from_form_to_config(main_config, form)
    assert main_config[SITE_TITLE] == test_title
    assert main_config[SITE_DESC] == placer_holder_text
    assert main_config[DATA_BACKEND] == POSTGRES


def test_graphic_dict_to_graphic_component_dict(graphic_json_fixture):
    test_config = graphic_json_fixture["graphic_1"]
    component_dict = graphic_dict_to_graphic_component_dict(test_config)
    assert component_dict[VISUALIZATION] == {
        "aggregate": {},
        "groupby": {},
        "hover_data": {},
    }
    assert component_dict[PLOTLY] == test_config[PLOT_SPECIFIC_INFO]
    selector_dict_expected = test_config[SELECTABLE_DATA_DICT]
    selector_dict_expected[NUMERICAL_FILTER] = []
    selector_dict_expected[FILTER] = []
    assert component_dict[SELECTOR] == test_config[SELECTABLE_DATA_DICT]
    test_config_copy = copy.deepcopy(test_config)
    # component_dict[GRAPHIC_META_INFO] contains all the data besides the keys
    # PLOT_SPECIFIC_INFO, SELECTABLE_DATA_DICT and VISUALIZATION_OPTIONS
    # test_config_copy does not contain VISUALIZATION_OPTIONS and we delete the other two.
    del test_config_copy[PLOT_SPECIFIC_INFO]
    del test_config_copy[SELECTABLE_DATA_DICT]
    test_config_copy[DATA_SOURCES][ADDITIONAL_DATA_SOURCES] = []
    assert component_dict[GRAPHIC_META_INFO] == test_config_copy


def test_graphic_component_dict_to_graphic_dict(graphic_json_fixture):
    test_config = graphic_json_fixture["graphic_1"]
    component_dict = graphic_dict_to_graphic_component_dict(test_config)
    new_test_config = graphic_component_dict_to_graphic_dict(component_dict)
    assert new_test_config == test_config


def test_get_data_source_info():
    assert False


def test_generate_collapse_dict_from_graphic_component_dict(graphic_json_fixture):
    test_config = graphic_json_fixture["graphic_0"]
    collapse_dict = generate_collapse_dict_from_graphic_component_dict(test_config)
    true_collapse_dict = {
        ADDITIONAL_DATA_SOURCES: True,
        HOVER_DATA: False,
        GROUPBY: False,
        AGGREGATE: True,
        FILTER: False,
        NUMERICAL_FILTER: False,
        AXIS: True,
        GROUPBY_SELECTOR: True,
        VISUALIZATION_OPTIONS: False,
        SELECTABLE_DATA_DICT: False,
    }
    assert collapse_dict == true_collapse_dict


def test_divide_columns_into_type_of_filters():
    column_types_dict = {
        "col_1": Integer(),
        "col_2": Text(),
        "col_3": Float(),
        "col_4": DateTime(),
        "col_5": ARRAY("string"),
        "col_6": Boolean(),
        "col_7": Integer(),
        "col_8": Float(),
        "col_9": DateTime(),
        "col_10": Text(),
        "col_11": Boolean(),
        "col_12": ARRAY("string"),
    }
    unique_entries = {
        "col_1": [1 for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR + 1)],
        "col_2": ["Dream" for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR - 1)],
        "col_3": [2.5 for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR + 1)],
        "col_4": ["11/10/2013" for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR + 1)],
        "col_5": [[1, 4, 5] for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR - 1)],
        "col_6": [True for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR - 1)],
        "col_7": [1 for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR - 1)],
        "col_8": [3.5 for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR - 1)],
        "col_9": ["11/10/2014" for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR - 1)],
        "col_10": ["Dream" for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR + 1)],
        "col_11": [True for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR + 1)],
        "col_12": [[1, 4, 5] for i in range(MAX_ENTRIES_FOR_FILTER_SELECTOR + 1)],
    }
    (
        filter_column_names,
        numerical_filter_column_names,
        unique_entries_dict,
    ) = divide_columns_into_type_of_filters(unique_entries, column_types_dict)
    assert set(numerical_filter_column_names) == {
        "col_1",
        "col_3",
        "col_4",
        "col_7",
        "col_8",
        "col_9",
    }
    filter_column_names_set = {"col_2", "col_5", "col_6", "col_7", "col_8", "col_9"}
    assert set(filter_column_names) == filter_column_names_set
    assert set(unique_entries_dict.keys()) == filter_column_names_set
    assert unique_entries_dict["col_2"] == unique_entries["col_2"]
    assert unique_entries_dict["col_5"] == unique_entries["col_5"]
    assert unique_entries_dict["col_6"] == unique_entries["col_6"]
    assert unique_entries_dict["col_7"] == unique_entries["col_7"]
    assert unique_entries_dict["col_8"] == unique_entries["col_8"]
    assert unique_entries_dict["col_9"] == unique_entries["col_9"]
