# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0


from abc import ABC, abstractmethod
from collections import defaultdict

from utility.available_selectors import AVAILABLE_SELECTORS
from parser import ParserError

from dateutil.parser import parse as datetime_parse
from utility.constants import *

NUMERICAL_FILTER_DICT = {MAX: "<=", MIN: ">="}


class Graphic(ABC):
    def __init__(self, graphic_dict: dict, addendum_dict: dict = None):

        """
        :param graphic_dict: Copy of part of the original config dict.
        Outside of getting the data, only functions in reformatting_functions.py should modifies the copy of config dict.
        :param addendum_dict: e.g ImmutableMultiDict([('graphic_name', 'graphic_0'), ('selection_0', 'SHOW_ALL_ROW'),
         ('selection_2_upper_operation', '<='), ('selection_2_upper_value', '4'))])
        Should not pass an empty ImmutableMultiDict
        """
        if addendum_dict is None:
            addendum_dict = {}
        self.graphic_dict = graphic_dict
        self.addendum_dict = addendum_dict
        self.select_info = []
        self.data = {}
        self.unique_entry_dict = {}
        self.graph_json_str = "{}"

    @staticmethod
    @abstractmethod
    def get_graph_html_template() -> str:
        """
        returns the graph html template the graphic library uses
        :param plot_options:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def make_dict_for_html_plot(self, data):
        """
        creates the json that is passed to the html template
        """
        raise NotImplementedError

    @abstractmethod
    def get_data_columns(self) -> set:
        """
        extracts what columns of data are needed from the self.graphic_dict[PLOT_SPECIFIC_INFO]
        :param plot_options:
        :return:
        """
        raise NotImplementedError

    def set_unique_entry_dict(self, unique_entry_dict):
        self.unique_entry_dict = unique_entry_dict

    def add_instructions_to_config_dict(self):
        if SELECTABLE_DATA_DICT in self.graphic_dict:
            self.add_active_selectors_to_selectable_data_list()
            if self.addendum_dict:
                self.add_operations_to_the_data_from_addendum()
            else:
                self.add_operations_to_the_data_from_defaults()
            self.modify_graphic_dict_based_on_addendum_dict()

    def add_active_selectors_to_selectable_data_list(self):
        """
        Sets which selectors are active based on user choices.
        If none have been selected sets reasonable defaults
        :return:
        """
        selectable_data_dict = self.graphic_dict[SELECTABLE_DATA_DICT]
        filter_list = selectable_data_dict.get(FILTER, [])
        for index, filter_dict in enumerate(filter_list):

            selected_filters = self.addendum_dict.get(
                get_key_for_form(FILTER, index), []
            )
            if SHOW_ALL_ROW in selected_filters:
                filter_dict[ACTIVE_SELECTORS] = [SHOW_ALL_ROW]
            else:
                filter_dict[ACTIVE_SELECTORS] = selected_filters or filter_dict.get(
                    DEFAULT_SELECTED, [SHOW_ALL_ROW]
                )

        numerical_filter_list = selectable_data_dict.get(NUMERICAL_FILTER, [])
        for index, numerical_filter_dict in enumerate(numerical_filter_list):
            extrema = [MAX, MIN]
            active_numerical_filter_dict = defaultdict(dict)
            for extremum in extrema:
                # pull the relevant filter info from the submitted form
                # all values in addendum_dict are lists
                numerical_filter_value = self.addendum_dict.get(
                    NUMERICAL_FILTER_NUM_LOC_TYPE.format(index, extremum, VALUE)
                )
                active_numerical_filter_dict[extremum][VALUE] = (
                    numerical_filter_value[0]
                    if numerical_filter_value
                    else numerical_filter_dict.get(extremum, "")
                )

            numerical_filter_dict[ACTIVE_SELECTORS] = active_numerical_filter_dict

    def add_operations_to_the_data_from_addendum(self):
        """
        Adds operations to be passed to the data handlers for the data
        Broken into two major parts read in info from selection_dict and addendum_dict and then
         output a filter dict or change visualization_info_list or data_info_dict depending on the kind of filter
        :selectable_data_dict: each element of the dictionary on is how to build the selector on the webpage
        :addendum_dict: User selections form the webpage
        :return:
        """
        selectable_data_dict = self.graphic_dict[SELECTABLE_DATA_DICT]
        operation_list = []

        # creates an operations where only the values selected along a column will be shown in the plot
        filter_list = selectable_data_dict.get(FILTER, [])
        for index, filter_dict in enumerate(filter_list):
            base_info_dict_for_selector = get_base_info_for_selector(
                filter_dict, FILTER
            )
            selection = self.addendum_dict.get(get_key_for_form(FILTER, index))
            if len(selection) == 0 or SHOW_ALL_ROW in selection:
                continue
            base_info_dict_for_selector[SELECTED] = selection
            base_info_dict_for_selector[FILTERED_SELECTOR] = filter_dict.get(
                FILTERED_SELECTOR, False
            )
            operation_list.append(base_info_dict_for_selector)

        # creates an operations where only the values following an (in)equality
        # along a column will be shown in the plot
        numerical_filter_list = selectable_data_dict.get(NUMERICAL_FILTER, [])
        for index, numerical_filter_dict in enumerate(numerical_filter_list):
            base_info_dict_for_selector = get_base_info_for_selector(
                numerical_filter_dict, NUMERICAL_FILTER
            )
            # the numerical filter contains two filters so add them separately
            for extremum in [MAX, MIN]:
                # get the value submitted in the web form by using its name
                # format specified in numeric_filter.html
                # the value is a list of length one
                numerical_value = self.addendum_dict[
                    NUMERICAL_FILTER_NUM_LOC_TYPE.format(index, extremum, VALUE)
                ][0]
                if numerical_value == "":
                    continue

                numerical_filter_info = {
                    VALUE: convert_string_for_numerical_filter(numerical_value),
                    OPERATION: NUMERICAL_FILTER_DICT[extremum],
                }
                operation_list.append(
                    {**base_info_dict_for_selector, **numerical_filter_info}
                )
        self.graphic_dict[DATA_FILTERS] = operation_list

    def add_operations_to_the_data_from_defaults(self):
        """
        Adds operations to be passed to the data handlers for the data
        Broken into two major parts read in info from selection_dict and then output a filter dict
        :selectable_data_dict: each filter element of the dict is a list of dictionary on how to build
        the selector on the webpage
        :return:
        """
        selectable_data_dict = self.graphic_dict[SELECTABLE_DATA_DICT]
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
                    base_info_dict_for_selector[FILTERED_SELECTOR] = filter_dict.get(
                        FILTERED_SELECTOR, False
                    )
                    operation_list.append(base_info_dict_for_selector)

        numerical_filter_list = selectable_data_dict.get(NUMERICAL_FILTER, [])
        for index, numerical_filter_dict in enumerate(numerical_filter_list):
            for extremum in [MAX, MIN]:
                numerical_value = numerical_filter_dict.get(extremum)
                if numerical_value == "" or numerical_value is None:
                    continue
                base_info_dict_for_selector = get_base_info_for_selector(
                    numerical_filter_dict, NUMERICAL_FILTER
                )
                numerical_filter_info = {
                    VALUE: convert_string_for_numerical_filter(numerical_value),
                    OPERATION: NUMERICAL_FILTER_DICT[extremum],
                }
                operation_list.append(
                    {**base_info_dict_for_selector, **numerical_filter_info}
                )
        if operation_list:
            self.graphic_dict[DATA_FILTERS] = operation_list

    def modify_graphic_dict_based_on_addendum_dict(self):
        """
        Subclass this method if a subclass has data selectors defined that should change hte graphic_dict
        See Plotly for an example
        """
        pass

    def get_columns_that_need_unique_entries(self) -> set:
        """
        extracts what data are needed for the selectors
        :param plot_options:
        :return:
        """
        filter_list = self.graphic_dict.get(SELECTABLE_DATA_DICT, {}).get(FILTER, [])
        column_list = [
            filter_dict[OPTION_COL]
            for filter_dict in filter_list
            if filter_dict.get(VISIBLE, True)
        ]
        return column_list

    def create_data_subselect_info_for_plot(self):
        """
        puts selector data in form to be read by html file
        Broken into two major parts read in info from selection_option_dict_for_plot and then populate
         select_info elements
        :param plot_specification:
        :param data_handler:
        :return:
        """

        selectable_data_dict = self.graphic_dict.get(SELECTABLE_DATA_DICT, {})

        filter_list = selectable_data_dict.get(FILTER, [])
        for index, filter_dict in enumerate(filter_list):
            if filter_dict.get(VISIBLE, True):
                column = filter_dict[OPTION_COL]

                selector_entries = self.unique_entry_dict[column]
                selector_entries.sort()
                # append show_all_rows to the front of the list
                selector_entries.insert(0, SHOW_ALL_ROW)
                self.select_info.append(
                    make_filter_dict(FILTER, filter_dict, index, selector_entries)
                )

        numerical_filter_list = selectable_data_dict.get(NUMERICAL_FILTER, [])
        for index, numerical_filter_dict in enumerate(numerical_filter_list):
            if numerical_filter_dict.get(VISIBLE, True):
                self.select_info.append(
                    make_filter_dict(NUMERICAL_FILTER, numerical_filter_dict, index)
                )


def get_key_for_form(selector_type, index):
    """
    We getting the div id based on string formatting here as set in make_filter_dict
    For example for selector_type=filter
    AVAILABLE_SELECTORS[selector_type][SELECTOR_NAME] is filter_{}
    :param selector_type:
    :param index:
    :return:
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


def make_filter_dict(selector_type, select_dict, index, selector_entries=None):
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
