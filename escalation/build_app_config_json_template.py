# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import json

from graphics.plotly_plot import (
    LAYOUT,
    AGGREGATIONS,
    AGGREGATE,
    HOVER_DATA,
    GROUPBY,
)
from utility.constants import *


def build_config_json_template():
    config_dict = {
        SITE_TITLE: "",
        SITE_DESC: "",
        DATA_BACKEND: "",
        AVAILABLE_PAGES: {
            "<page_identifier_goes_here_no_spaces>": {
                WEBPAGE_LABEL: "<page name>",
                GRAPHICS: {
                    "<graphic_identifier_goes_here_no_spaces>": {
                        PLOT_MANAGER: "plotly",
                        DATA_SOURCES: [{DATA_SOURCE_TYPE: ""}],
                        GRAPHIC_TITLE: "",
                        GRAPHIC_DESC: "",
                        DATA: {
                            POINTS_NUM.format(0): {"<axis>": "", "<another axis>": "",}
                        },
                        PLOT_SPECIFIC_INFO: {
                            DATA: [{"type": "<e.g. scatter>"}],
                            LAYOUT: {},
                        },
                        VISUALIZATION_OPTIONS: [
                            {OPTION_TYPE: HOVER_DATA, COLUMN_NAME: ["", "",],},
                            {
                                OPTION_TYPE: GROUPBY,
                                COLUMN_NAME: [""],
                                SELECT_OPTION: {"styles": {},},
                            },
                            {
                                OPTION_TYPE: AGGREGATE,
                                COLUMN_NAME: [""],
                                SELECT_OPTION: {
                                    AGGREGATIONS: {"<axis>": "<function e.g. avg>",}
                                },
                            },
                        ],
                        SELECTABLE_DATA_DICT: [
                            {
                                OPTION_TYPE: "select",
                                COLUMN_NAME: "",
                                SELECT_OPTION: {"multiple": False},
                            },
                            {OPTION_TYPE: NUMERICAL_FILTER, COLUMN_NAME: "",},
                        ],
                    },
                },
            }
        },
    }
    return config_dict


if __name__ == "__main__":
    config_dict = build_config_json_template()
    with open("config_template.json", "w") as fout:
        json.dump(config_dict, fout, indent=4)
