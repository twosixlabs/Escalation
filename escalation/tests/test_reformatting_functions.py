# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import copy

import pytest
from werkzeug.datastructures import ImmutableMultiDict

from tests.conftest import make_graphic_config_for_testing
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
    VISUALIZATION_OPTIONS,
    FILTER,
    NUMERICAL_FILTER,
    GROUPBY,
    AXIS,
    COLUMN_NAME,
    PLOT_SPECIFIC_INFO,
)
from utility.reformatting_functions import (
    add_operations_to_the_data_from_addendum,
    add_active_selectors_to_selectable_data_list,
    add_instructions_to_config_dict,
    get_key_for_form,
)


@pytest.fixture()
def single_page_config_dict():
    config_dict = make_graphic_config_for_testing()
    single_page_config_dict = copy.deepcopy(config_dict)

    return single_page_config_dict


@pytest.fixture()
def addendum_dict():
    addendum_dict = ImmutableMultiDict(
        [
            ("graphic_name", "graphic_0"),
            ("filter_0", "MALE"),
            ("filter_1", "Torgersen"),
            ("filter_1", "Dream"),
            ("numerical_filter_0_upper_operation", ">"),
            ("numerical_filter_0_upper_value", "4"),
            ("numerical_filter_0_lower_operation", ">="),
            ("numerical_filter_0_lower_value", ""),
        ]
    )
    return addendum_dict


def test_add_active_selectors_to_selectable_data_list_with_addendum(
    single_page_config_dict, addendum_dict
):
    graphic_0_dict = single_page_config_dict["graphic_0"]
    add_active_selectors_to_selectable_data_list(
        graphic_0_dict[SELECTABLE_DATA_DICT],
        graphic_0_dict[PLOT_SPECIFIC_INFO][DATA],
        addendum_dict,
    )
    filter_list = graphic_0_dict[SELECTABLE_DATA_DICT][FILTER]
    assert len(filter_list[0][ACTIVE_SELECTORS]) == 1
    assert "MALE" in filter_list[0][ACTIVE_SELECTORS]
    assert len(filter_list[1][ACTIVE_SELECTORS]) == 2
    assert "Torgersen" in filter_list[1][ACTIVE_SELECTORS]
    assert "Dream" in filter_list[1][ACTIVE_SELECTORS]

    numerical_filter_list = graphic_0_dict[SELECTABLE_DATA_DICT][NUMERICAL_FILTER]
    assert numerical_filter_list[0][ACTIVE_SELECTORS][UPPER_INEQUALITY][VALUE] == "4"
    assert (
        numerical_filter_list[0][ACTIVE_SELECTORS][UPPER_INEQUALITY][OPERATION] == ">"
    )


def test_add_active_selectors_to_selectable_data_list_with_SHOW_ALL_ROWS_chosen_with_others(
    single_page_config_dict,
):
    addendum_dict = ImmutableMultiDict(
        [
            ("graphic_name", "graphic_0"),
            ("filter_0", "MALE"),
            ("filter_1", "Torgersen"),
            ("filter_1", "Dream"),
            ("filter_1", SHOW_ALL_ROW),
            ("numerical_filter_0_upper_operation", ">"),
            ("numerical_filter_0_upper_value", "4"),
            ("numerical_filter_0_lower_operation", ">="),
            ("numerical_filter_0_lower_value", ""),
        ]
    )
    graphic_0_dict = single_page_config_dict["graphic_0"]
    add_active_selectors_to_selectable_data_list(
        graphic_0_dict[SELECTABLE_DATA_DICT],
        graphic_0_dict[PLOT_SPECIFIC_INFO][DATA],
        addendum_dict,
    )
    assert len(graphic_0_dict[SELECTABLE_DATA_DICT][FILTER][1][ACTIVE_SELECTORS]) == 1
    assert (
        SHOW_ALL_ROW
        in graphic_0_dict[SELECTABLE_DATA_DICT][FILTER][1][ACTIVE_SELECTORS]
    )


def test_add_active_selectors_to_selectable_data_list_without_addendum(
    single_page_config_dict,
):
    single_page_config_dict = single_page_config_dict
    graphic_0_dict = single_page_config_dict["graphic_0"]
    add_active_selectors_to_selectable_data_list(
        graphic_0_dict[SELECTABLE_DATA_DICT],
        graphic_0_dict[PLOT_SPECIFIC_INFO][DATA],
        ImmutableMultiDict(),
    )

    filter_list = graphic_0_dict[SELECTABLE_DATA_DICT][FILTER]
    assert len(filter_list[0][ACTIVE_SELECTORS]) == 1
    assert SHOW_ALL_ROW in filter_list[0][ACTIVE_SELECTORS]
    assert len(filter_list[1][ACTIVE_SELECTORS]) == 1
    assert SHOW_ALL_ROW in filter_list[1][ACTIVE_SELECTORS]

    numerical_filter_list = graphic_0_dict[SELECTABLE_DATA_DICT][NUMERICAL_FILTER]
    assert numerical_filter_list[0][ACTIVE_SELECTORS][UPPER_INEQUALITY][VALUE] == ""
    assert (
        numerical_filter_list[0][ACTIVE_SELECTORS][UPPER_INEQUALITY][OPERATION] == "<="
    )


def test_add_operations_to_the_data(single_page_config_dict, addendum_dict):
    single_page_config_dict = single_page_config_dict
    graphic_0_dict = single_page_config_dict["graphic_0"]
    operations_list, groupby_dict = add_operations_to_the_data_from_addendum(
        graphic_0_dict[SELECTABLE_DATA_DICT],
        graphic_0_dict[PLOT_SPECIFIC_INFO][DATA],
        addendum_dict,
    )
    assert not groupby_dict
    assert len(operations_list) == 3

    assert operations_list[0] == {
        "type": "filter",
        "column": "penguin_size:sex",
        "selected": ["MALE"],
    }
    assert operations_list[1] == {
        "type": "filter",
        "column": "penguin_size:island",
        "selected": ["Torgersen", "Dream"],
    }
    assert operations_list[2] == {
        "type": "numerical_filter",
        "column": "penguin_size:culmen_length_mm",
        "operation": ">",
        "value": 4.0,
    }

    # test two

    graphic_1_dict = single_page_config_dict["graphic_1"]
    addendum_dict = ImmutableMultiDict(
        [
            ("graphic_index", "graphic_1"),
            ("axis_0", "penguin_size:culmen_depth_mm"),
            (GROUPBY, "penguin_size:island"),
        ]
    )

    operations_list, groupby_dict = add_operations_to_the_data_from_addendum(
        graphic_1_dict[SELECTABLE_DATA_DICT],
        graphic_1_dict[PLOT_SPECIFIC_INFO][DATA],
        addendum_dict,
    )

    assert (
        single_page_config_dict[GRAPHIC_NUM.format(1)][PLOT_SPECIFIC_INFO][DATA][0]["x"]
        == "penguin_size:culmen_depth_mm"
    )
    assert groupby_dict == {
        COLUMN_NAME: ["penguin_size:island"],
    }


def test_add_instructions_to_config_dict(single_page_config_dict, addendum_dict):
    single_page_config_dict = single_page_config_dict
    single_page_config_dict_test = copy.deepcopy(single_page_config_dict)
    single_page_config_dict_test = add_instructions_to_config_dict(
        single_page_config_dict_test, None
    )
    # add instructions should call the other two methods which I am already testing for.
    # So I want to make sure it in actually doing something
    assert single_page_config_dict_test != single_page_config_dict
    assert DATA_FILTERS not in single_page_config_dict_test[GRAPHIC_NUM.format(0)]

    single_page_config_dict_test = copy.deepcopy(single_page_config_dict)
    single_page_config_dict_test = add_instructions_to_config_dict(
        single_page_config_dict_test, addendum_dict
    )
    assert DATA_FILTERS in single_page_config_dict_test[GRAPHIC_NUM.format(0)]


def test_add_instructions_to_config_dict_with_different_addendum(
    single_page_config_dict,
):
    single_page_config_dict = single_page_config_dict
    single_page_config_dict_test = copy.deepcopy(single_page_config_dict)
    addendum_dict = ImmutableMultiDict(
        [
            ("graphic_name", "a_different_graph"),
            ("filter_0", "MALE"),
            ("filter_1", "Torgersen"),
            ("filter_1", "Dream"),
            ("numerical_filter_0_upper_operation", ">"),
            ("numerical_filter_0_upper_value", "4"),
            ("numerical_filter_0_lower_operation", ">="),
            ("numerical_filter_0_lower_value", ""),
        ]
    )
    single_page_config_dict_test = add_instructions_to_config_dict(
        single_page_config_dict_test, addendum_dict
    )
    graphic_0_dict = single_page_config_dict_test["graphic_0"]
    assert len(graphic_0_dict[SELECTABLE_DATA_DICT][FILTER][0][ACTIVE_SELECTORS]) == 1
    assert (
        SHOW_ALL_ROW
        in graphic_0_dict[SELECTABLE_DATA_DICT][FILTER][0][ACTIVE_SELECTORS]
    )


def test_get_key_for_form():
    assert "filter_1" == get_key_for_form(FILTER, 1)
    assert "numerical_filter_4" == get_key_for_form(NUMERICAL_FILTER, 4)
    assert "groupby" == get_key_for_form(GROUPBY, "")
    assert "axis_0" == get_key_for_form(AXIS, 0)
