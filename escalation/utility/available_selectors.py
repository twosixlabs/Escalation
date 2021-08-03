# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

# selectors are dropdowns, checkboxes etc.
from utility.constants import *
from parser import ParserError

from dateutil.parser import parse as datetime_parse

AVAILABLE_SELECTORS = {
    "filter": {
        SELECT_HTML_TEMPLATE: "selector.html",
        TEXT: "Filter by {}",
        SELECTOR_NAME: "filter_{}",
    },
    "groupby": {
        SELECT_HTML_TEMPLATE: "selector.html",
        TEXT: "Group by:",
        SELECTOR_NAME: "groupby",
    },
    "match": {
        SELECT_HTML_TEMPLATE: "match.html",
        TEXT: "Match in {}",
        SELECTOR_NAME: "match_{}",
    },
    "numerical_filter": {
        SELECT_HTML_TEMPLATE: "numerical_filter.html",
        TEXT: "Filter by {}",
        SELECTOR_NAME: "numerical_filter_{}",
    },
    "filter_range": {
        SELECT_HTML_TEMPLATE: "filter_range.html",
        TEXT: "Filter by {}",
        SELECTOR_NAME: "filter_range_{}",
    },
}


def get_key_for_form(selector_type, index):
    """
    We getting the div id based on string formatting here as set in make_filter_dict
    For example for selector_type=filter
    AVAILABLE_SELECTORS[selector_type][SELECTOR_NAME] is filter_{}
    """
    selection_index_str = AVAILABLE_SELECTORS[selector_type][SELECTOR_NAME].format(
        index
    )
    return selection_index_str


def convert_string_for_numerical_filter(value: str):
    try:
        return float(value)
    except ValueError:
        try:
            return datetime_parse(value)
        except ParserError:
            raise (ValueError, "neither a float nor a datetime")


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
    return base_info_dict_for_selector


def make_filter_dict(selector_type, select_dict, index=0, selector_entries=None):
    """
    Reformats convenient Python data structures into a dict easily parsed in Jinja

    See tests/test_controller test cases for example formats of the inputs and outputs of this function

    :param selector_type: one of AXIS, FILTER, GROUPBY, NUMERICAL_FILTER (see the explicit iteration in create_data_subselect_info_for_plot)
    :param select_dict:
    :param index: form index corresponds to  ordering of selectors on the web interface
    :param selector_entries: A list of options to include in UI dropdown
    :return: dict structured for read by Jinja
    """
    html_filter_dict = {SELECTOR_TYPE: selector_type}
    selector_attributes = AVAILABLE_SELECTORS[selector_type]
    column = select_dict.get(OPTION_COL, "")
    html_filter_dict[JINJA_SELECT_HTML_FILE] = selector_attributes[SELECT_HTML_TEMPLATE]
    html_filter_dict[SELECTOR_NAME] = selector_attributes[SELECTOR_NAME].format(index)
    html_filter_dict[TEXT] = selector_attributes[TEXT].format(column)
    html_filter_dict[ACTIVE_SELECTORS] = select_dict[ACTIVE_SELECTORS]
    html_filter_dict[TYPE] = select_dict.get(TYPE, "")
    html_filter_dict[MULTIPLE] = select_dict.get(MULTIPLE, False)
    html_filter_dict[ENTRIES] = selector_entries
    return html_filter_dict
