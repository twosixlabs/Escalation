# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
from graphics.graphic_schema import GraphicsConfigInterfaceBuilder
from utility.constants import *
from utility.schema_utils import conditional_dict


class BootstrapTableSchema(GraphicsConfigInterfaceBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_individual_plot_type_schema(self, plot_type):
        schema = {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            TITLE: "Bootstrap Table Config",
            DESCRIPTION: "Makes a table",
            TYPE: OBJECT,
            REQUIRED: [COLUMNS],
            PROPERTIES: {
                COLUMNS: {
                    DESCRIPTION: "List of columns names",
                    TYPE: ARRAY_STRING,
                    ITEMS: {
                        TYPE: OBJECT,
                        TITLE: "Column",
                        REQUIRED: [FIELD],
                        PROPERTIES: {
                            FIELD: {
                                TYPE: STRING,
                                DESCRIPTION: "Name of the columns in the data",
                                **conditional_dict(
                                    ENUM, self.data_holder.possible_column_names
                                ),
                            },
                            TITLE: {
                                TYPE: STRING,
                                DESCRIPTION: "Shown column name on the table, defaults to field",
                            },
                            FORMATTER: {
                                TITLE: "Data Formatter",
                                DESCRIPTION: "Format string data or use prewritten functions to show images",
                                ANYOF: [
                                    {TYPE: NULL, TITLE: "None"},
                                    {
                                        TYPE: STRING,
                                        TITLE: "Prewritten Functions",
                                        ENUM: ["img_url_to_img"],
                                        DESCRIPTION: "Used to show images",
                                    },
                                    {
                                        TYPE: STRING,
                                        TITLE: "Write Your Own",
                                        DESCRIPTION: "For example - ID: %s",
                                    },
                                ],
                            },
                        },
                    },
                },
                SEARCH: {TYPE: BOOLEAN, DEFAULT: False},
                PAGINATION: {TYPE: BOOLEAN, DEFAULT: False},
            },
        }

        return schema

    @staticmethod
    def get_available_plots():
        return [{GRAPHIC_NAME: "Bootstrap Table", VALUE: "btable"}]
