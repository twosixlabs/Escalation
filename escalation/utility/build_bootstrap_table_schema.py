# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy

from graphics.plotly_plot import LAYOUT
from utility.constants import *


TABLE = "table"
HEADER = "header"
SELECTOR_DICT = {
    TABLE: "Table",
}


def build_table_schema(column_names):
    if column_names:
        column_names.sort()
    schema = {
        "$schema": "http://json-schema.org/draft/2019-09/schema#",
        "title": "bootstrap table definition",
        "description": "dictionary that uses https://bootstrap-table.com/",
        "type": "object",
        "required": [DATA],
        "properties": {
            DATA: {
                "type": "array",
                TITLE: "List of Columns",
                "description": "list of columns in the table",
                MIN_ITEMS: 1,
                "items": {
                    "type": "object",
                    "title": "Column Information",
                    "required": [HEADER, COLUMN_NAME],
                    "properties": {
                        HEADER: {"type": "string", TITLE: "Column Header",},
                        COLUMN_NAME: {
                            "type": "string",
                            TITLE: "Column name in database",
                            "enum": column_names,
                        },
                    },
                },
            },
            OPTIONS: {
                "title": "Table options",
                "description": "currently not implemented, see https://bootstrap-table.com/",
                "type": "object",
            },
        },
    }
    return schema
