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
    GROUPBY_SELECTOR,
    MAX_ENTRIES_FOR_FILTER_SELECTOR,
    AVAILABLE_PAGES,
    WEBPAGE_LABEL,
    URL_ENDPOINT,
    GRAPHIC_CONFIG_FILES,
    GRAPHIC_PATH,
    GRAPHIC,
    VISUALIZATION_OPTIONS,
)
from utility.wizard_utils import (
    invert_dict_lists,
    sanitize_string,
    extract_data_sources_from_config,
    copy_data_from_form_to_config,
    graphic_dict_to_graphic_component_dict,
    graphic_component_dict_to_graphic_dict,
    get_layout_for_dashboard,
)

from sqlalchemy.types import Integer, Text, Float, DateTime, ARRAY, Boolean


def test_invert_dict_lists():
    test_dict = {"a": [1], "b": [2, 3]}
    expected_dict = {1: "a", 2: "b", 3: "b"}
    inverted_dict = invert_dict_lists(test_dict)
    assert inverted_dict == expected_dict


def test_get_layout_for_dashboard(main_json_sql_backend_fixture):
    # app context
    # mapper_dict = get_layout_for_dashboard(main_json_sql_backend_fixture[AVAILABLE_PAGES])

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
    #            URL_ENDPOINT: "radio_penguins",
    #             GRAPHIC_CONFIG_FILES: ["radio_penguins.json"],
    #         },
    #     ],
    # )
    # assert mapper_dict == ground_truth
    assert False


def test_sanitize_string():
    test_string = r"this! i:/\s*$. test 42"
    sanitized = r"this_is_test_42"
    assert sanitize_string(test_string) == sanitized


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
    test_config = graphic_json_fixture["graphic_0"]
    component_dict = graphic_dict_to_graphic_component_dict(test_config)
    assert component_dict[GRAPHIC] == test_config[PLOT_SPECIFIC_INFO]
    selector_dict_expected = test_config[SELECTABLE_DATA_DICT]
    assert component_dict[SELECTOR] == test_config[SELECTABLE_DATA_DICT]
    test_config_copy = copy.deepcopy(test_config)
    # component_dict[GRAPHIC_META_INFO] contains all the data besides the keys
    # PLOT_SPECIFIC_INFO, SELECTABLE_DATA_DICT and VISUALIZATION_OPTIONS
    # test_config_copy does not contain VISUALIZATION_OPTIONS and we delete the other two.
    del test_config_copy[PLOT_SPECIFIC_INFO]
    del test_config_copy[SELECTABLE_DATA_DICT]
    assert component_dict[GRAPHIC_META_INFO] == test_config_copy


def test_graphic_component_dict_to_graphic_dict(graphic_json_fixture):
    test_config = graphic_json_fixture["graphic_1"]
    component_dict = graphic_dict_to_graphic_component_dict(test_config)
    new_test_config = graphic_component_dict_to_graphic_dict(component_dict)
    assert new_test_config == test_config
