# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from collections import defaultdict

from werkzeug.datastructures import ImmutableMultiDict

from utility.available_selectors import AVAILABLE_SELECTORS
from utility.constants import *

NUMERICAL_FILTER_DEFAULT = {
    UPPER_INEQUALITY: {OPERATION: "<=", VALUE: ""},
    LOWER_INEQUALITY: {OPERATION: ">=", VALUE: ""},
}


def add_instructions_to_config_dict(
    single_page_graphic_config_dict: dict, addendum_dict: dict = None
) -> dict:
    """
    We build a page based on 2 dictonaries, what is in the config and what is submitted in the HTML form.
    :param single_page_graphic_config_dict: Copy of part of the original config dict.
    Outside of getting the data, only functions in reformatting_functions.py should modifies the copy of config dict.
    :param addendum_dict: e.g ImmutableMultiDict([('graphic_name', 'graphic_0'), ('selection_0', 'SHOW_ALL_ROW'),
     ('selection_2_upper_operation', '<='), ('selection_2_upper_value', '4'))])
    Should not pass an empty ImmutableMultiDict
    :return: modified single_page_config_dict
    """
    if addendum_dict is None:
        addendum_dict = {}

    for graphic_name, graphic_dict in single_page_graphic_config_dict.items():
        if SELECTABLE_DATA_DICT in graphic_dict:
            selector_dict = graphic_dict[SELECTABLE_DATA_DICT]
            data_info_dict = graphic_dict[PLOT_SPECIFIC_INFO][DATA]
            if graphic_name in addendum_dict:
                add_active_selectors_to_selectable_data_list(
                    selector_dict, data_info_dict, addendum_dict[graphic_name]
                )
                (
                    graphic_dict[DATA_FILTERS],
                    groupby_dict,
                ) = add_operations_to_the_data_from_addendum(
                    selector_dict, data_info_dict, addendum_dict[graphic_name],
                )
                # Visualization options does not have to be in the dictionary
                if groupby_dict:
                    visualization_info_dict = graphic_dict.get(
                        VISUALIZATION_OPTIONS, {}
                    )
                    visualization_info_dict[GROUPBY] = groupby_dict
                    graphic_dict[VISUALIZATION_OPTIONS] = visualization_info_dict
            else:
                add_active_selectors_to_selectable_data_list(
                    selector_dict, data_info_dict
                )
                data_filters = add_operations_to_the_data_from_defaults(selector_dict)
                if data_filters:
                    graphic_dict[DATA_FILTERS] = data_filters
    return single_page_graphic_config_dict


def add_active_selectors_to_selectable_data_list(
    selectable_data_dict: dict, data_info_dict: dict, addendum_dict: dict = None,
):
    """
    Sets which selectors are active based on user choices.
    If none have been selected sets reasonable defaults
    :param selectable_data_dict: each element of the dictionary is a list of dictionaries
     on how to build the selector on the webpage
    :param data_info_dict: Dictionary that has which data goes in which plot
    :param addendum_dict: User selections form the webpage
    :return:
    """

    if addendum_dict is None:
        addendum_dict = {}

    axis_list = selectable_data_dict.get(AXIS, [])
    for index, axis_dict in enumerate(axis_list):
        # all values in addendum_dict are lists
        axis_label = addendum_dict.get(get_key_for_form(AXIS, index))
        axis_dict[ACTIVE_SELECTORS] = (
            axis_label[0] if axis_label else data_info_dict[0][axis_dict[COLUMN_NAME]]
        )

    if GROUPBY in selectable_data_dict:
        group_by_dict = selectable_data_dict[GROUPBY]
        selected_group_by = addendum_dict.get(get_key_for_form(GROUPBY, ""))
        if not selected_group_by or NO_GROUP_BY in selected_group_by:
            group_by_dict[ACTIVE_SELECTORS] = [NO_GROUP_BY]
        else:
            group_by_dict[ACTIVE_SELECTORS] = selected_group_by or group_by_dict.get(
                DEFAULT_SELECTED, [NO_GROUP_BY]
            )

    filter_list = selectable_data_dict.get(FILTER, [])
    for index, filter_dict in enumerate(filter_list):

        selected_filters = addendum_dict.get(get_key_for_form(FILTER, index), [])
        if SHOW_ALL_ROW in selected_filters:
            filter_dict[ACTIVE_SELECTORS] = [SHOW_ALL_ROW]
        else:
            filter_dict[ACTIVE_SELECTORS] = selected_filters or filter_dict.get(
                DEFAULT_SELECTED, [SHOW_ALL_ROW]
            )

    numerical_filter_list = selectable_data_dict.get(NUMERICAL_FILTER, [])
    for index, numerical_filter_dict in enumerate(numerical_filter_list):
        locations = [UPPER_INEQUALITY, LOWER_INEQUALITY]
        active_numerical_filter_dict = defaultdict(dict)
        for loc in locations:
            for input_type in [OPERATION, VALUE]:
                # pull the relevant filter info from the submitted form
                # all values in addendum_dict are lists
                numerical_filter_value = addendum_dict.get(
                    NUMERICAL_FILTER_NUM_LOC_TYPE.format(index, loc, input_type)
                )
                active_numerical_filter_dict[loc][input_type] = (
                    numerical_filter_value[0]
                    if numerical_filter_value
                    else NUMERICAL_FILTER_DEFAULT[loc][input_type]
                )

        numerical_filter_dict[ACTIVE_SELECTORS] = active_numerical_filter_dict


def add_operations_to_the_data_from_addendum(
    selectable_data_dict: dict, data_info_list: list, addendum_dict: dict,
) -> list:
    """
    Adds operations to be passed to the data handlers for the data
    Broken into two major parts read in info from selection_dict and addendum_dict and then
     output a filter dict or change visualization_info_list or data_info_dict depending on the kind of filter
    :param selectable_data_dict: each element of the dictionary on is how to build the selector on the webpage
    :param data_info_list: Dictionary that has which data goes in which plot
    :param visualization_info_dict: dict of visualization options
    :param addendum_dict: User selections form the webpage
    :return:
    """
    groupby_dict = {}
    operation_list = []

    # modifies the axis shown in the config
    axis_list = selectable_data_dict.get(AXIS, [])
    for index, axis_dict in enumerate(axis_list):
        new_column_for_axis = addendum_dict.get(get_key_for_form(AXIS, index))[0]
        axis = axis_dict[COLUMN_NAME]
        for axis_data_dict in data_info_list:
            axis_data_dict[axis] = new_column_for_axis

    # adds a group by
    if GROUPBY in selectable_data_dict:
        selection = addendum_dict.get(get_key_for_form(GROUPBY, ""))
        if len(selection) > 0 and NO_GROUP_BY not in selection:
            groupby_dict = {COLUMN_NAME: selection}

    # creates an operations where only the values selected along a column will be shown in the plot
    filter_list = selectable_data_dict.get(FILTER, [])
    for index, filter_dict in enumerate(filter_list):
        base_info_dict_for_selector = get_base_info_for_selector(filter_dict, FILTER)
        selection = addendum_dict.get(get_key_for_form(FILTER, index))
        if len(selection) == 0 or SHOW_ALL_ROW in selection:
            continue
        base_info_dict_for_selector[SELECTED] = selection
        operation_list.append(base_info_dict_for_selector)

    # creates an operations where only the values following an (in)equality
    # along a column will be shown in the plot
    numerical_filter_list = selectable_data_dict.get(NUMERICAL_FILTER, [])
    for index, numerical_filter_dict in enumerate(numerical_filter_list):
        base_info_dict_for_selector = get_base_info_for_selector(
            numerical_filter_dict, NUMERICAL_FILTER
        )
        # the numerical filter contains two filters so add them separately
        for loc in [UPPER_INEQUALITY, LOWER_INEQUALITY]:
            # get the value submitted in the web form by using its name
            # format specified in numeric_filter.html
            # the value is a list of length one
            numerical_value = addendum_dict[
                NUMERICAL_FILTER_NUM_LOC_TYPE.format(index, loc, VALUE)
            ][0]
            if numerical_value == "":
                continue
            numerical_filter_info = {
                VALUE: float(numerical_value),
                OPERATION: addendum_dict[
                    NUMERICAL_FILTER_NUM_LOC_TYPE.format(index, loc, OPERATION)
                ][0],
            }
            operation_list.append(
                {**base_info_dict_for_selector, **numerical_filter_info}
            )
    return operation_list, groupby_dict


def add_operations_to_the_data_from_defaults(selectable_data_dict: dict) -> list:
    """
    Adds operations to be passed to the data handlers for the data
    Broken into two major parts read in info from selection_dict and then output a filter dict
    :param selectable_data_dict: each filter element of the dict is a list of dictionary on how to build
    the selector on the webpage
    :return:
    """
    operation_list = []
    filter_list = selectable_data_dict.get(FILTER, [])
    for index, filter_dict in enumerate(filter_list):
        if DEFAULT_SELECTED in filter_dict:
            base_info_dict_for_selector = get_base_info_for_selector(
                filter_dict, FILTER
            )
            selection = filter_dict.get(DEFAULT_SELECTED)
            # make sure we don't have an empty selection list,
            #  or a list that only contains an empty string
            if selection and selection != [""]:
                base_info_dict_for_selector[SELECTED] = (
                    selection if isinstance(selection, list) else [selection]
                )
                operation_list.append(base_info_dict_for_selector)

    return operation_list


def get_base_info_for_selector(selection_dict, selector_type):
    """
    Sets up the basic dictionary for data filters to be added on the data
    :param selection_dict:
    :param selector_type:
    :return:
    """
    base_info_dict_for_selector = {
        OPTION_TYPE: selector_type,
        COLUMN_NAME: selection_dict.get(COLUMN_NAME, ""),
    }
    if UNFILTERED_SELECTOR in selection_dict:
        base_info_dict_for_selector[UNFILTERED_SELECTOR] = True
    return base_info_dict_for_selector


def get_key_for_form(selector_type, index):
    selection_index_str = AVAILABLE_SELECTORS[selector_type][SELECTOR_NAME].format(
        index
    )
    return selection_index_str


def add_form_to_addendum_dict(form: ImmutableMultiDict, addendum_dict: dict):
    """
    Used to update the addendum_dict that contains the previous graphic
     selection elements with a new set of selections from a posted form
    :param form:
    :param addendum_dict:
    :return:
    """
    graphic_dict = {}
    for key, value in form.lists():
        if key in [GRAPHIC_NAME, PROCESS]:
            continue
        graphic_dict[key] = value
    addendum_dict[form.get(GRAPHIC_NAME)] = graphic_dict
