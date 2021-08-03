import itertools

from graphics.available_graphics import AVAILABLE_GRAPHICS

from database.available_backends import AVAILABLE_BACKEND_SCHEMAS
from utility.constants import *
from flask import current_app

from utility.schema_utils import SchemaDataHolder

KEY_FILTER = "key_filter"


# json schema specific constants see https://json-schema.org/


def build_dashboard_layout_schema():
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
                "enum": [POSTGRES],
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


class ConfigInterfaceBuilder:
    def __init__(self, plot_manager, backend, active_data_source_names=None):

        self.data_holder = SchemaDataHolder(active_data_source_names)
        self.data_holder.get_data_source_info()
        self.data_holder.sort_data()

        self.data_config = AVAILABLE_BACKEND_SCHEMAS[backend](self.data_holder)

        if plot_manager in AVAILABLE_GRAPHICS:
            graphic_schema_class = AVAILABLE_GRAPHICS[plot_manager][SCHEMA_CLASS]
            self.graphic_config = graphic_schema_class(self.data_holder)
        else:
            raise ValueError(f"plot_manager {plot_manager} not recognized")

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
                    "enum": list(AVAILABLE_GRAPHICS.keys()),
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
                DATA_SOURCES: {
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
        return schema

    def build_visualization_options(self):
        """
        Schema that changes the layout of the figure on the dashboard page
        :return:
        """
        schema = {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            TYPE: OBJECT,
            TITLE: "Visualization Options",
            DESCRIPTION: "These options change the layout of the figure on the dashboard page",
            PROPERTIES: {
                HEIGHT: {
                    TYPE: INTEGER,
                    DESCRIPTION: "Height of the graphic in pixels",
                    DEFAULT: 400,
                    MINIMUM: 0,
                }
            },
        }
        return schema

    def build_graphic_schemas_for_ui(self, plot_type):
        """
        Builds 4 separate schemas to be used by the UI:
        GRAPHIC_SCHEMA contains information specific to the plot as configured
        PLOT_MANAGER_SCHEMA contains the overall schema from the plot_manager- e.g., Plotly's scatterplot schema
        VISUALIZATION_SCHEMA contains the VISUALIZATION_OPTIONS dict describing graph-specific configured visualization choices
        SELECTOR_SCHEMA has different plot types available
        :return: a dict read by the wizard HTML jinja template
        """

        ui_configurer_schema = {
            GRAPHIC_SCHEMA: self.build_header_schema(),
            PLOT_MANAGER_SCHEMA: self.graphic_config.build_individual_plot_type_schema(
                plot_type
            ),
            SELECTOR_SCHEMA: self.data_config.build_data_filter_schema(),
            VISUALIZATION_SCHEMA: self.build_visualization_options(),
        }
        return ui_configurer_schema
