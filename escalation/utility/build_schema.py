# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import json
from collections import defaultdict

from graphics.plotly_plot import STYLES
from utility.build_plotly_schema import build_plotly_schema
from utility.constants import *

NO_DOTS = r"^[^\\.]*$"
ALPHA_NUMERIC_NO_SPACES = r"^[a-zA-Z0-9_]+$"
ONE_DOT = r"^[^\\.]*\\.[^\\.]*$"
ONE_LETTER = r"^[a-zA-Z]$"
NON_EMPTY_STRING = r"[\s\S]+"

# json schema specific constants see https://json-schema.org/


def build_settings_schema():
    schema = {
        "$schema": "http://json-schema.org/draft/2019-09/schema#",
        "title": "Escalation Main Config Generator",
        "description": "Main config file needed to use escalation OS",
        "type": "object",
        REQUIRED: [SITE_TITLE, SITE_DESC, DATA_BACKEND],
        "additionalProperties": False,
        "properties": {
            SITE_TITLE: {
                "type": "string",
                TITLE: "Site Title",
                "description": "title shown at the top of the website",
            },
            SITE_DESC: {
                "type": "string",
                "title": "Site Description",
                "description": "description shown at the top of the website",
            },
            DATA_BACKEND: {
                "type": "string",
                TITLE: "Data Backend",
                "description": "How the data is being managed on the server",
                "enum": [POSTGRES, LOCAL_CSV],
            },
            AVAILABLE_PAGES: {
                "type": "array",
                TITLE: "Webpages",
                DESCRIPTION: "array of webpages",
                ITEMS: {
                    "type": "object",
                    TITLE: "Page",
                    REQUIRED: [WEBPAGE_LABEL, URL_ENDPOINT],
                    PROPERTIES: {
                        WEBPAGE_LABEL: {
                            "type": "string",
                            TITLE: "Label",
                            DESCRIPTION: "UI label of the webpage",
                        },
                        URL_ENDPOINT: {
                            "type": "string",
                            TITLE: "URL",
                            DESCRIPTION: "Endpoint of a url",
                            PATTERN: ALPHA_NUMERIC_NO_SPACES,
                        },
                        GRAPHIC_CONFIG_FILES: {
                            TYPE: "array",
                            TITLE: "Graphic Config Files",
                            ITEMS: {
                                TYPE: "string",
                                TITLE: "Config File",
                                DESCRIPTION: "Path to config file of the graphic for the webpage",
                            },
                        },
                    },
                },
            },
        },
    }
    return schema


def build_graphic_schema(
    data_source_names=None, column_names=None, unique_entries=None, collapse_dict=None
):
    """

    :param data_source_names: names from DATA_SOURCES, already checked against the file system
    :param column_names: possible column names from files or database (format data_source_name.column_name)
    :param unique_entries: values from possible column names
    :param collapse_dict: whether the element should be collapsed or not
    :return:
    """
    if not collapse_dict:
        collapse_dict = defaultdict(lambda: True)
    if data_source_names:
        data_source_names.sort()
    if column_names:
        column_names.sort()
    if unique_entries:
        unique_entries.sort()
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
                "description": "plot library you would like to use"
                " (only plotly is currently available)",
                "enum": ["plotly"],
            },
            GRAPHIC_TITLE: {
                "type": "string",
                TITLE: "Graph Title",
                PATTERN: NON_EMPTY_STRING,
            },
            GRAPHIC_DESC: {
                "type": "string",
                TITLE: "Graph Description",
                "description": "Text caption shown above the graph (optional)",
            },
            DATA_SOURCES: {
                "type": "object",
                TITLE: "Data Sources",
                "description": "Define which data tables are used in this graphic,"
                " and on which columns the data tables are joined",
                "required": [MAIN_DATA_SOURCE],
                OPTIONS: {DISABLE_COLLAPSE: True, DISABLE_PROPERTIES: True},
                PROPERTIES: {
                    MAIN_DATA_SOURCE: {
                        TITLE: "Main Data Source",
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
                        OPTIONS: {COLLAPSED: collapse_dict[ADDITIONAL_DATA_SOURCES],},
                        ITEMS: {
                            "type": "object",
                            TITLE: "Additional Data Source",
                            "additionalProperties": False,
                            REQUIRED: [DATA_SOURCE_TYPE, JOIN_KEYS],
                            PROPERTIES: {
                                DATA_SOURCE_TYPE: {
                                    "type": "string",
                                    TITLE: "Data Source Type",
                                    "enum": data_source_names,
                                },
                                JOIN_KEYS: {
                                    "type": "array",
                                    TITLE: "Join Keys",
                                    "description": "Column names along which to join the tables"
                                    " (in the case of 2 or more tables)",
                                    ITEMS: {
                                        TITLE: "Pairs of Keys",
                                        DESCRIPTION: "Use the command/ctr key to select more than one entry",
                                        "type": "array",
                                        "uniqueItems": True,
                                        "minItems": 2,
                                        "maxItems": 2,
                                        "items": {
                                            "type": "string",
                                            TITLE: "Key",
                                            "enum": column_names,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            PLOT_SPECIFIC_INFO: {
                "type": "object",
                "title": "Plot Dictionary",
                "description": "this dictionary depends on the graphing library",
            },
            VISUALIZATION_OPTIONS: {
                "type": "object",
                "title": "Visualization Options",
                "description": "Graph options: hover tooltips, aggregation functions, group by",
                "additionalProperties": False,
                OPTIONS: {
                    COLLAPSED: collapse_dict[VISUALIZATION_OPTIONS],
                    REMOVE_EMPTY_PROPERTIES: True,
                },
                PROPERTIES: {
                    HOVER_DATA: {
                        "type": "object",
                        "title": "Hover Data",
                        "description": "data shown on hover over by mouse",
                        "required": [COLUMN_NAME],
                        OPTIONS: {COLLAPSED: collapse_dict[HOVER_DATA]},
                        "properties": {
                            COLUMN_NAME: {
                                "type": "array",
                                TITLE: "List of Column Names",
                                OPTIONS: {DISABLE_COLLAPSE: True},
                                "items": {
                                    "type": "string",
                                    TITLE: "Column Name",
                                    "enum": column_names,
                                },
                            }
                        },
                    },
                    GROUPBY: {
                        "type": "object",
                        "title": "Group By",
                        "description": "Grouping of the data see https://plotly.com/javascript/group-by/",
                        "required": [COLUMN_NAME],
                        OPTIONS: {
                            COLLAPSED: collapse_dict[GROUPBY],
                            REMOVE_EMPTY_PROPERTIES: True,
                        },
                        "properties": {
                            COLUMN_NAME: {
                                "type": "array",
                                TITLE: "List of Column Names",
                                OPTIONS: {DISABLE_COLLAPSE: True},
                                "items": {
                                    "type": "string",
                                    TITLE: "Column Name",
                                    "enum": column_names,
                                },
                            },
                            STYLES: {
                                TYPE: "object",
                                TITLE: "Styles",
                                DESCRIPTION: "Optional, see https://plotly.com/javascript/group-by/ for examples",
                                OPTIONS: {COLLAPSED: True},
                            },
                        },
                    },
                    AGGREGATE: {
                        "type": "object",
                        "title": "Aggregate",
                        "description": "See https://plotly.com/javascript/aggregations/ for examples",
                        "required": [COLUMN_NAME, AGGREGATIONS],
                        OPTIONS: {COLLAPSED: collapse_dict[AGGREGATE]},
                        "properties": {
                            COLUMN_NAME: {
                                "type": "array",
                                TITLE: "List of Column Names",
                                OPTIONS: {DISABLE_COLLAPSE: True},
                                "items": {
                                    "type": "string",
                                    TITLE: "Column Name",
                                    "enum": column_names,
                                },
                            },
                            AGGREGATIONS: {
                                "type": "object",
                                TITLE: "Aggregations",
                                "description": "axis to function on the data e.g. x:avg",
                                OPTIONS: {DISABLE_COLLAPSE: True},
                                "patternProperties": {
                                    ONE_LETTER: {
                                        "type": "string",
                                        "description": "function on the data",
                                        "enum": [
                                            "avg",
                                            "sum",
                                            "min",
                                            "max",
                                            "mode",
                                            "median",
                                            "count",
                                            "stddev",
                                            "first",
                                            "last",
                                        ],
                                    }
                                },
                            },
                        },
                    },
                },
            },
            SELECTABLE_DATA_DICT: {
                "type": "object",
                "title": "Data Selector Options",
                "description": "Interactive data selectors: filter data by values, change axes,"
                " change columns to group by",
                ADDITIONAL_PROPERTIES: False,
                OPTIONS: {
                    COLLAPSED: collapse_dict[SELECTABLE_DATA_DICT],
                    REMOVE_EMPTY_PROPERTIES: True,
                },
                PROPERTIES: {
                    FILTER: {
                        "type": "array",
                        "title": "List of Filters",
                        DESCRIPTION: "a filter operation based on label",
                        OPTIONS: {COLLAPSED: collapse_dict[FILTER]},
                        "items": {
                            "type": "object",
                            TITLE: "Filter",
                            "id": "filter_item",
                            "required": [COLUMN_NAME],
                            "additionalProperties": False,
                            OPTIONS: {DISABLE_COLLAPSE: True},
                            PROPERTIES: {
                                COLUMN_NAME: {
                                    "type": "string",
                                    TITLE: "Column Name",
                                    "description": "name in table",
                                    "enum": column_names,
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
                                                "source": unique_entries,
                                                "filter": "default_selected_filter",
                                                "title": "identity_callback",
                                                "value": "identity_callback",
                                            }
                                        ],
                                    },
                                },
                                UNFILTERED_SELECTOR: {
                                    "type": "boolean",
                                    TITLE: "Should Selector Be Filtered",
                                    DESCRIPTION: "If selector is filtered, the user can only select values in this"
                                    " field that are present in the data subsetted by the"
                                    " currently-applied filters",
                                },
                            },
                        },
                    },
                    NUMERICAL_FILTER: {
                        "type": "array",
                        "title": "List of Numerical Filters",
                        DESCRIPTION: "a filter operation on numerical data",
                        OPTIONS: {COLLAPSED: collapse_dict[NUMERICAL_FILTER]},
                        "items": {
                            TITLE: "Numerical Filters",
                            "type": "object",
                            "required": [COLUMN_NAME],
                            OPTIONS: {DISABLE_COLLAPSE: True},
                            "additionalProperties": False,
                            PROPERTIES: {
                                COLUMN_NAME: {
                                    "type": "string",
                                    TITLE: "Column Name",
                                    "description": "name in table",
                                    "enum": column_names,
                                }
                            },
                        },
                    },
                    AXIS: {
                        "type": "array",
                        "title": "List of Axis Selectors",
                        DESCRIPTION: "change what column data is shown on a axis",
                        OPTIONS: {COLLAPSED: collapse_dict[AXIS]},
                        "items": {
                            "type": "object",
                            TITLE: "Axis Selector",
                            OPTIONS: {DISABLE_COLLAPSE: True},
                            "required": [COLUMN_NAME, ENTRIES],
                            "additionalProperties": False,
                            PROPERTIES: {
                                COLUMN_NAME: {
                                    "type": "string",
                                    TITLE: "Axis Name",
                                    "pattern": ONE_LETTER,
                                },
                                ENTRIES: {
                                    "type": "array",
                                    TITLE: "Entries",
                                    "items": {"type": "string", "enum": column_names,},
                                },
                            },
                        },
                    },
                    GROUPBY: {
                        "type": "object",
                        "title": "Group By Selector",
                        "required": [ENTRIES],
                        OPTIONS: {COLLAPSED: collapse_dict[GROUPBY_SELECTOR]},
                        "additionalProperties": False,
                        PROPERTIES: {
                            ENTRIES: {
                                "type": "array",
                                OPTIONS: {DISABLE_COLLAPSE: True},
                                TITLE: "Entries",
                                "items": {"type": "string", "enum": column_names},
                            },
                            "multiple": {"type": "boolean"},
                            DEFAULT_SELECTED: {
                                "type": "array",
                                TITLE: "Default Selected",
                                "description": "optional, default filter, list of column values",
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    }
    return schema


def build_graphic_schema_with_plotly(data_source_names=None, column_names=None):
    """
    If you are using the app with plotly this puts the plotly schema into the graphic schema
    :param data_source_names:
    :param column_names:
    :return:
    """
    schema = build_graphic_schema(data_source_names, column_names)
    plotly_schema = build_plotly_schema(column_names)
    schema[PROPERTIES][PLOT_SPECIFIC_INFO] = plotly_schema
    return schema


def convert_python_dict_to_schema_json_file():
    """
    Makes the schema dictionaries into files (currently only used for generating documentation)
    :return:
    """
    for file_name, schema_dict in zip(
        ["main.schema.json", "graphic.schema.json"],
        [build_settings_schema(), build_graphic_schema_with_plotly()],
    ):
        json_object = json.dumps(schema_dict, indent=4)
        with open(file_name, "w") as outfile:
            outfile.write(json_object)


if __name__ == "__main__":
    # if the schema is needed as a json file
    convert_python_dict_to_schema_json_file()
