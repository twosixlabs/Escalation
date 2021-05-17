# Copyright [2021] [Two Six Labs, LLC],
# Licensed under the Apache License, Version 2.0,

from abc import ABC, abstractmethod
import itertools

from flask import current_app
from sqlalchemy import Integer, Float, DateTime

from utility.constants import *

KEY_FILTER = "key_filter"


def build_data_sources_schema(data_source_names, possible_column_names, hidden):
    data_sources_schema = {
        "type": "object",
        TITLE: "Data Sources",
        "description": "Define which data tables are used in this graphic,"
        " and on which columns the data tables are joined",
        "required": [MAIN_DATA_SOURCE],
        OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True, HIDDEN: hidden},
        PROPERTIES: {
            MAIN_DATA_SOURCE: {
                TITLE: "Main Data Source",
                "id": MAIN_DATA_SOURCE,
                "type": "object",
                "additionalProperties": False,
                REQUIRED: [DATA_SOURCE_TYPE],
                PROPERTIES: {
                    DATA_SOURCE_TYPE: {
                        "type": "string",
                        TITLE: "Data Source Type",
                        "enum": data_source_names,
                    },
                },
                OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True},
            },
            ADDITIONAL_DATA_SOURCES: {
                "type": "array",
                TITLE: "Additional Data Sources",
                ITEMS: {
                    "type": "object",
                    TITLE: "Additional Data Source",
                    "additionalProperties": False,
                    "id": ADDITIONAL_DATA_SOURCES,
                    REQUIRED: [DATA_SOURCE_TYPE, JOIN_KEYS],
                    OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True},
                    PROPERTIES: {
                        DATA_SOURCE_TYPE: {
                            "type": "string",
                            TITLE: "Data Source Type",
                            "enum": data_source_names,
                        },
                        # Tuple validation (json-schema.org/understanding-json-schema/reference/array.html?highlight=default#tuple-validation)
                        # may be faster on the browser side and is the 'correct' way to use JSON schema
                        JOIN_KEYS: {
                            "type": "array",
                            TITLE: "Join Keys",
                            "description": "Column names along which to join the tables"
                            " (in the case of 2 or more tables)",
                            ITEMS: {
                                TITLE: "Pairs of Keys",
                                DESCRIPTION: "First key from a previous data source"
                                " and second key from the data source being added",
                                "type": "array",
                                "uniqueItems": True,
                                MIN_ITEMS: 2,
                                MAX_ITEMS: 2,
                                "items": {
                                    "type": "string",
                                    TITLE: "Key",
                                    "watch": {
                                        MAIN_DATA_SOURCE: ".".join(
                                            [MAIN_DATA_SOURCE, DATA_SOURCE_TYPE]
                                        ),
                                        ADDITIONAL_DATA_SOURCES: ".".join(
                                            [ADDITIONAL_DATA_SOURCES, DATA_SOURCE_TYPE]
                                        ),
                                    },
                                    "enumSource": [
                                        {
                                            "source": possible_column_names,
                                            "filter": KEY_FILTER,
                                            "title": CALLBACK,
                                            "value": CALLBACK,
                                        }
                                    ],
                                },
                            },
                        },
                    },
                },
            },
        },
    }
    return data_sources_schema


def get_data_sources():
    data_inventory_class = current_app.config.data_backend_writer
    data_sources = data_inventory_class.get_available_data_sources()
    return data_sources


def get_data_sources_and_column_names():
    """
    used for populating the data source schema in the wizard landing page
    :return:
    """
    data_sources = get_data_sources()
    possible_column_names, _, _ = get_possible_column_names_and_values(
        data_sources, get_types=False, get_unique_values=False
    )
    return data_sources, possible_column_names


def get_possible_column_names_and_values(
    data_sources, get_types=True, get_unique_values=True
):
    """
    Used to populate a dropdown in the config wizard with any column from the data
    sources included in a figure, unique_entries used to populate default selected.
    :param data_source_names: list of data source name strings
    :param get_types: if true calculates the type of each column
    :param get_unique_values: if true calculates unique values for each column
    """
    possible_column_names = []
    unique_entries = {}
    column_types_dict = {}
    data_handler_class = current_app.config.data_handler
    for data_source_name in data_sources:
        data_inventory = data_handler_class(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source_name}}
        )
        column_names_for_data_source = data_inventory.get_column_names_for_data_source()

        possible_column_names.extend(column_names_for_data_source)
        if get_types:
            column_types_dict_for_data_source = (
                data_inventory.get_schema_for_data_source()
            )
            column_types_dict.update(column_types_dict_for_data_source)
        if get_unique_values:
            unique_entries_for_data_source = data_inventory.get_column_unique_entries(
                column_names_for_data_source
            )
            unique_entries.update(unique_entries_for_data_source)
    return possible_column_names, unique_entries, column_types_dict


class GraphicsConfigInterfaceBuilder(ABC):
    def __init__(self, collapse_dict=None, active_data_source_names=None):
        if active_data_source_names is None:
            self.active_data_source_names = []
        else:
            self.active_data_source_names = active_data_source_names

        # set by get_data_source_info
        self.data_source_names = None
        # set by divide_columns_into_type_of_filters called by get_data_source_info
        self.filter_column_names = []
        self.numerical_filter_column_names = []
        # set by get_possible_column_names_and_values called by get_data_source_info
        # todo: rename as data_source_column_names?
        self.possible_column_names = None
        self.column_types_dict = None
        self.unique_entries_dict = None
        self.unique_entry_values_list = None

        # todo set defaultdict with true?
        self.collapse_dict = collapse_dict

        # defined in subclass. Todo: require it be defined
        self.plot_selector_dict = None

        self.get_data_source_info()

    def build_header_schema(self):
        schema = {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "type": "object",
            "title": "Escalation Graphic Config Generator",
            "description": "This form configures a single graphic",
            "required": [
                PLOT_MANAGER,
                GRAPHIC_TITLE,
                GRAPHIC_DESC,
                DATA_SOURCES,
                PLOT_SPECIFIC_INFO,
            ],
            "additionalProperties": False,
            OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True},
            PROPERTIES: {
                PLOT_MANAGER: {
                    "type": "string",
                    TITLE: "Plot Backend",
                    "description": "plot library you would like to use",
                    "enum": PLOT_MANAGERS,
                    OPTIONS: {HIDDEN: True,},
                },
                PLOT_TYPE: {
                    "type": "string",
                    TITLE: "Plot Type",
                    "description": "Which plot manager schema does PLOT_SPECIFIC_INFO follow",
                    OPTIONS: {HIDDEN: True,},
                },
                GRAPHIC_TITLE: {
                    "type": "string",
                    TITLE: "Graph Title",
                    DEFAULT: "<Graph Title>",
                    PATTERN: NON_EMPTY_STRING,
                },
                GRAPHIC_DESC: {
                    "type": "string",
                    TITLE: "Graph Description",
                    "description": "Text caption shown above the graph (optional)",
                },
                PLOT_SPECIFIC_INFO: {
                    "type": "object",
                    "title": "Plot Dictionary",
                    "description": "this dictionary depends on the graphing library",
                    OPTIONS: {
                        DISABLE_COLLAPSE: True,
                        DISABLE_PROPERTIES: True,
                        HIDDEN: True,
                    },
                },
            },
        }

        schema[PROPERTIES][DATA_SOURCES] = build_data_sources_schema(
            self.data_source_names, self.possible_column_names, True
        )
        return schema

    @staticmethod
    def get_wizard_data_source_schema():
        data_sources, possible_column_names = get_data_sources_and_column_names()
        return build_data_sources_schema(data_sources, possible_column_names, False)

    def build_data_filter_schema(self):
        selectable_data_schema = {
            "type": "object",
            "title": "Data Selector Options",
            "description": "Interactive data selectors: filter data by values, change axes,"
            " change columns to group by",
            ADDITIONAL_PROPERTIES: False,
            OPTIONS: {
                COLLAPSED: self.collapse_dict[SELECTABLE_DATA_DICT],
                REMOVE_EMPTY_PROPERTIES: True,
            },
            PROPERTIES: {
                FILTER: {
                    "type": "array",
                    "title": "List of Filters",
                    DESCRIPTION: "a filter operation based on label",
                    OPTIONS: {COLLAPSED: self.collapse_dict[FILTER]},
                    "items": {
                        "type": "object",
                        TITLE: "Filter",
                        "id": "filter_item",
                        "required": [COLUMN_NAME],
                        "additionalProperties": False,
                        OPTIONS: {DISABLE_COLLAPSE: True},
                        PROPERTIES: {
                            VISIBLE: {
                                TYPE: "boolean",
                                DEFAULT: True,
                                DESCRIPTION: "Determines whether or not the filter dropdown is visible to the user.",
                            },
                            COLUMN_NAME: {
                                "type": "string",
                                TITLE: "Column Name",
                                "description": "any data column with fewer than 200 unique entries can be filtered"
                                " by identity matching and is listed here",
                                "enum": self.filter_column_names,
                            },
                            "multiple": {
                                "type": "boolean",
                                TITLE: "Allow Multiple Selections",
                                DESCRIPTION: "Allow multiple values to be selected in this filter",
                            },
                            DEFAULT_SELECTED: {
                                "type": "array",
                                TITLE: "Default Selected",
                                "description": "Optional, Default value(s) selected in this filter,"
                                " a list of values to include",
                                "items": {
                                    "type": "string",
                                    # watch will call the functions in enumSource (default_selected_filter,
                                    # identity_callback; defined in the JS) whenever COLUMN_NAME is changed,
                                    # it will also store the value of COLUMN_NAME to a variable called COLUMN_NAME
                                    #  to be used by the JS
                                    "watch": {
                                        COLUMN_NAME: ".".join(
                                            ["filter_item", COLUMN_NAME]
                                        )
                                    },
                                    "enumSource": [
                                        {
                                            "source": self.unique_entry_values_list,
                                            "filter": COLUMN_VALUE_FILTER,
                                            "title": CALLBACK,
                                            "value": CALLBACK,
                                        }
                                    ],
                                },
                            },
                            FILTERED_SELECTOR: {
                                "type": "boolean",
                                TITLE: "Should Selector Be Filtered",
                                DESCRIPTION: "If selector is filtered, the user can only select values in this"
                                " field that are present in the data subsetted by the"
                                " currently-applied filters",
                                DEFAULT: False,
                            },
                        },
                    },
                },
                NUMERICAL_FILTER: {
                    "type": "array",
                    "title": "List of Numerical Filters",
                    DESCRIPTION: "a filter operation on numerical data",
                    OPTIONS: {COLLAPSED: self.collapse_dict[NUMERICAL_FILTER]},
                    "items": {
                        TITLE: "Numerical Filters",
                        "type": "object",
                        "required": [COLUMN_NAME, TYPE],
                        OPTIONS: {DISABLE_COLLAPSE: True},
                        "additionalProperties": False,
                        PROPERTIES: {
                            VISIBLE: {
                                TYPE: "boolean",
                                DEFAULT: True,
                                DESCRIPTION: "Determines whether or not the numerical filter dropdown"
                                " is visible to the user.",
                            },
                            COLUMN_NAME: {
                                "type": "string",
                                TITLE: "Column Name",
                                "description": "name in table",
                                "enum": self.numerical_filter_column_names,
                            },
                            TYPE: {
                                TYPE: "string",
                                DESCRIPTION: "number or datetime",
                                DEFAULT: "number",
                                ENUM: ["number", DATETIME],
                            },
                            MAX: {
                                TITLE: "Default Maximum",
                                "description": "Optional, set null for no max",
                                ONEOF: [
                                    {"type": "null"},
                                    {"type": "number"},
                                    {"type": "string", "format": "datetime-local"},
                                ],
                            },
                            MIN: {
                                TITLE: "Default Minimum",
                                "description": "Optional, set null for no min",
                                ONEOF: [
                                    {"type": "null"},
                                    {"type": "number"},
                                    {"type": "string", "format": "datetime-local"},
                                ],
                            },
                        },
                    },
                },
            },
        }
        return selectable_data_schema

    @abstractmethod
    def build_individual_plot_type_schema(self, plot_type):
        # must be implemented in subclass for graphic library
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_available_plots():
        """
        :return:An array of dictionaries with two keys:
        Name: shown name to the user
        Value: name of the schema, input to build_individual_plot_type_schema
        """
        raise NotImplementedError

    def sort_data(self):
        for info_list in [
            self.data_source_names,
            self.possible_column_names,
            self.filter_column_names,
            self.numerical_filter_column_names,
            self.unique_entry_values_list,
        ]:
            if info_list:
                info_list.sort()

    def get_possible_column_names_and_values(self, get_unique_values=True):
        """
        Used to populate a dropdown in the config wizard with any column from the data
        sources included in a figure, unique_entries used to populate default selected.
        :param data_source_names: list of data source name strings
        :param data_handler_class: backend-specific data inventory class
        :param get_unique_values: if true calculates unique values for each column
        """
        (
            possible_column_names,
            unique_entries,
            column_types_dict,
        ) = get_possible_column_names_and_values(
            self.active_data_source_names, get_unique_values=get_unique_values
        )
        self.unique_entries_dict = unique_entries
        self.possible_column_names = possible_column_names
        self.column_types_dict = column_types_dict
        self.unique_entry_values_list = self.get_unique_entries_as_single_list()

    def get_data_source_info(self):
        """
        gets the available data sources and the possible column names based on the data source in the config
        :return:
        """
        self.data_source_names = get_data_sources()
        self.active_data_source_names = [
            data_source_name
            for data_source_name in self.active_data_source_names
            if data_source_name in self.data_source_names
        ]
        if self.data_source_names and not self.active_data_source_names:
            # default to the first in alphabetical order
            self.active_data_source_names = [min(self.data_source_names)]

        self.get_possible_column_names_and_values()
        self.divide_columns_into_type_of_filters()

    def divide_columns_into_type_of_filters(self):
        """
        We only allow numerical data types to be filtered with a numerical inequality filter,
        and any data column with fewer than MAX_ENTRIES_FOR_FILTER_SELECTOR unique entries
        to be filtered by identity matching
        """
        numerical_types = [Integer, Float, DateTime]

        unique_entries_dict_copy = {}
        for col_name, list_of_entries in self.unique_entries_dict.items():
            if any(
                [
                    isinstance(self.column_types_dict[col_name], num_type)
                    for num_type in numerical_types
                ]
            ):
                self.numerical_filter_column_names.append(col_name)
            if len(list_of_entries) <= MAX_ENTRIES_FOR_FILTER_SELECTOR:
                self.filter_column_names.append(col_name)
                unique_entries_dict_copy[col_name] = list_of_entries
        self.unique_entries_dict = unique_entries_dict_copy

    def build_graphic_schemas_for_ui(self, plot_type):
        """
        Builds 4 separate schemas to be used by the UI:
        GRAPHIC_SCHEMA contains information specific to the plot as configured
        PLOT_MANAGER_SCHEMA contains the overall schema from the plot_manager- e.g., Plotly's scatterplot schema
        VISUALIZATION_SCHEMA contains the VISUALIZATION_OPTIONS dict describing graph-specific configured visualization choices
        SELECTOR_SCHEMA has different plot types available
        :return: a dict read by the wizard HTML jinja template
        """
        self.sort_data()
        ui_configurer_schema = {
            GRAPHIC_SCHEMA: self.build_header_schema(),
            PLOT_MANAGER_SCHEMA: self.build_individual_plot_type_schema(plot_type),
            SELECTOR_SCHEMA: self.build_data_filter_schema(),
        }
        return ui_configurer_schema

    def get_unique_entries_as_single_list(self):
        # concatenating into one large list with no duplicates
        unique_entries_list = list(
            set(itertools.chain.from_iterable(self.unique_entries_dict.values()))
        )
        return unique_entries_list
