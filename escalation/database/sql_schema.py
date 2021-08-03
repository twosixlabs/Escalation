from sqlalchemy import Integer, Float, DateTime

from database.data_schema import DataConfigInterfaceBuilder
from utility.constants import *
from utility.schema_utils import conditional_dict

KEY_FILTER = "key_filter"


class SqlConfigInterfaceBuilder(DataConfigInterfaceBuilder):
    @staticmethod
    def build_data_sources_schema(data_source_names, possible_column_names):
        data_sources_schema = {
            "type": "object",
            TITLE: "Data Sources",
            "description": "Define which data tables are used in this graphic,"
            " and on which columns the data tables are joined",
            "required": [MAIN_DATA_SOURCE],
            OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True},
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
                            **conditional_dict(ENUM, data_source_names),
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
                                **conditional_dict(ENUM, data_source_names),
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
                                        **(
                                            {
                                                "watch": {
                                                    MAIN_DATA_SOURCE: ".".join(
                                                        [
                                                            MAIN_DATA_SOURCE,
                                                            DATA_SOURCE_TYPE,
                                                        ]
                                                    ),
                                                    ADDITIONAL_DATA_SOURCES: ".".join(
                                                        [
                                                            ADDITIONAL_DATA_SOURCES,
                                                            DATA_SOURCE_TYPE,
                                                        ]
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
                                            }
                                            if possible_column_names
                                            else {}
                                        ),
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }
        return data_sources_schema

    def build_data_filter_schema(self):
        selectable_data_schema = {
            "type": "object",
            "title": "Data Selector Options",
            "description": "Interactive data selectors - e.g. filter data by values.",
            ADDITIONAL_PROPERTIES: False,
            OPTIONS: {REMOVE_EMPTY_PROPERTIES: True,},
            DEFAULT_PROPERTIES: [FILTER, NUMERICAL_FILTER],
            PROPERTIES: {
                FILTER: {
                    "type": "array",
                    "title": "List of Filters",
                    DESCRIPTION: "a filter operation based on label",
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
                                **conditional_dict(
                                    ENUM, self.data_holder.filter_dict[FILTER]
                                ),
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
                                    **(
                                        {
                                            "watch": {
                                                COLUMN_NAME: ".".join(
                                                    ["filter_item", COLUMN_NAME]
                                                )
                                            },
                                            "enumSource": [
                                                {
                                                    "source": self.data_holder.unique_entry_values_list,
                                                    "filter": COLUMN_VALUE_FILTER,
                                                    "title": CALLBACK,
                                                    "value": CALLBACK,
                                                }
                                            ],
                                        }
                                        if self.data_holder.unique_entry_values_list
                                        else {}
                                    ),
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
                                **conditional_dict(
                                    ENUM, self.data_holder.filter_dict[NUMERICAL_FILTER]
                                ),
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
