import json
import os

from utility.constants import *


def build_config_json(data_backend, data_file_directory):
    config_dict = {
        SITE_TITLE: "Escalation Test",
        "brief_desc": "This is a test/demo for the Escalation OS",
        DATA_BACKEND: data_backend,
        DATA_FILE_DIRECTORY: data_file_directory,
        DATA_SOURCES: ["penguin_size", "mean_penguin_stat", "penguin_size_small"],
        AVAILABLE_PAGES: [
            {
                WEBPAGE_LABEL: "PENGUINS!",
                URL_ENDPOINT: "penguin",
                GRAPHIC_CONFIG_FILES: ["big_penguins.json", "hist_penguins.json",],
            },
            {
                WEBPAGE_LABEL: "Radio Penguins",
                URL_ENDPOINT: "radio_penguins",
                GRAPHIC_CONFIG_FILES: ["radio_penguins.json"],
            },
        ],
    }
    return config_dict


def build_config_json_graphic_big_penguins():
    config_file = {
        PLOT_MANAGER: "plotly",
        DATA_SOURCES: [{DATA_SOURCE_TYPE: "penguin_size"}],
        GRAPHIC_TITLE: "Do massive penguins have long flippers?",
        GRAPHIC_DESC: "This plot looks at the relationship between...",
        PLOT_SPECIFIC_INFO: {
            DATA: [
                {
                    "type": "scatter",
                    "x": "penguin_size:body_mass_g",
                    "y": "penguin_size:flipper_length_mm",
                    "mode": "markers",
                }
            ]
        },
        VISUALIZATION_OPTIONS: {
            HOVER_DATA: {
                COLUMN_NAME: ["penguin_size:species", "penguin_size:culmen_length_mm",],
            },
            GROUPBY: {COLUMN_NAME: ["penguin_size:sex", "penguin_size:island"],},
        },
        SELECTABLE_DATA_DICT: {
            FILTER: [
                {COLUMN_NAME: "penguin_size:sex", MULTIPLE: False,},
                {
                    COLUMN_NAME: "penguin_size:island",
                    MULTIPLE: True,
                    DEFAULT_SELECTED: ["Dream"],
                },
            ],
            NUMERICAL_FILTER: [{COLUMN_NAME: "penguin_size:culmen_length_mm"}],
        },
    }
    return config_file


def build_config_json_graphic_hist_penguins():
    config_file = {
        PLOT_MANAGER: "plotly",
        DATA_SOURCES: [{DATA_SOURCE_TYPE: "penguin_size"}],
        GRAPHIC_TITLE: "How big are penguins?",
        GRAPHIC_DESC: "Try the group by selector",
        PLOT_SPECIFIC_INFO: {
            DATA: [
                {"type": "histogram", "x": "penguin_size:body_mass_g", "opacity": 0.5}
            ],
            LAYOUT: {"barmode": "overlay", "yaxis": {"title": {"text": "count"}},},
        },
        SELECTABLE_DATA_DICT: {
            AXIS: [
                {
                    COLUMN_NAME: "x",
                    ENTRIES: [
                        "penguin_size:culmen_length_mm",
                        "penguin_size:flipper_length_mm",
                        "penguin_size:body_mass_g",
                        "penguin_size:culmen_depth_mm",
                    ],
                },
            ],
            GROUPBY: {
                ENTRIES: ["penguin_size:sex", "penguin_size:island"],
                MULTIPLE: True,
            },
        },
    }
    return config_file


def build_config_json_graphic_radio_penguins():
    config_file = {
        PLOT_MANAGER: "plotly",
        DATA_SOURCES: [
            {DATA_SOURCE_TYPE: "penguin_size"},
            {
                DATA_SOURCE_TYPE: "mean_penguin_stat",
                JOIN_KEYS: [
                    ("penguin_size:study_name", "mean_penguin_stat:study_name",),
                    ("penguin_size:sex", "mean_penguin_stat:sex"),
                    ("penguin_size:species", "mean_penguin_stat:species",),
                ],
            },
        ],
        GRAPHIC_TITLE: "Can we join tables to find whether radio isotopes are connected to penguin size?",
        GRAPHIC_DESC: "",
        PLOT_SPECIFIC_INFO: {
            DATA: [
                {
                    "type": "scatter",
                    "x": "penguin_size:culmen_length_mm",
                    "y": "mean_penguin_stat:delta_15_n",
                    "mode": "markers",
                }
            ]
        },
        VISUALIZATION_OPTIONS: {
            HOVER_DATA: {
                COLUMN_NAME: ["penguin_size:sex", "penguin_size:culmen_length_mm",],
            },
            GROUPBY: {COLUMN_NAME: ["penguin_size:sex"],},
            AGGREGATE: {
                COLUMN_NAME: ["mean_penguin_stat:delta_15_n"],
                AGGREGATIONS: {"y": "avg"},
            },
        },
        SELECTABLE_DATA_DICT: {
            AXIS: [
                {
                    COLUMN_NAME: "x",
                    ENTRIES: [
                        "penguin_size:culmen_length_mm",
                        "penguin_size:flipper_length_mm",
                        "penguin_size:body_mass_g",
                        "penguin_size:culmen_depth_mm",
                    ],
                },
                {
                    COLUMN_NAME: "y",
                    ENTRIES: [
                        "mean_penguin_stat:delta_15_n",
                        "mean_penguin_stat:delta_13_c",
                    ],
                },
            ]
        },
    }
    return config_file


# todo: don't assume we're running the script from escalation directory?
if __name__ == "__main__":
    PATH_TO_GRAPHIC_CONFIG_FILES = "path_to_graphic_config_files"
    path_to_test_files = os.path.join("test_app_deploy_data")
    config_file_definitions = {
        "test_app_local_config.json": {DATA_BACKEND: LOCAL_CSV,},
        "test_app_sql_config.json": {DATA_BACKEND: POSTGRES},
    }

    for config_file_name, config in config_file_definitions.items():
        config_dict = build_config_json(**config)
        test_config_file_path = os.path.join(path_to_test_files, config_file_name)
        with open(test_config_file_path, "w") as fout:
            json.dump(config_dict, fout, indent=4)

    with open(os.path.join(path_to_test_files, "big_penguins.json"), "w") as fout:
        json.dump(build_config_json_graphic_big_penguins(), fout, indent=4)

    with open(os.path.join(path_to_test_files, "hist_penguins.json"), "w") as fout:
        json.dump(build_config_json_graphic_hist_penguins(), fout, indent=4)

    with open(os.path.join(path_to_test_files, "radio_penguins.json"), "w") as fout:
        json.dump(build_config_json_graphic_radio_penguins(), fout, indent=4)
