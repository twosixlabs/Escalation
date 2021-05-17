# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from utility.constants import *


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
