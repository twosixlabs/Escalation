import copy
import json
import os
import re

from flask import current_app

from utility.constants import *

UI_SCHEMA_PAIRS = {
    SELECTOR: SELECTABLE_DATA_DICT,
    GRAPHIC: PLOT_SPECIFIC_INFO,
    VISUALIZATION: VISUALIZATION_OPTIONS,
}


def save_main_config_dict(config_dict):
    main_config_path = os.path.join(current_app.config[CONFIG_FILE_FOLDER], MAIN_CONFIG)
    if os.path.exists(main_config_path):
        os.remove(main_config_path)
    with open(main_config_path, "w") as fout:
        json.dump(config_dict, fout, indent=4)


def load_main_config_dict_if_exists(app):
    try:
        with open(
            os.path.join(app.config[CONFIG_FILE_FOLDER], MAIN_CONFIG), "r"
        ) as config_file:
            config_dict = json.load(config_file)
        return config_dict
    except (OSError, IOError):
        return {}


def load_graphic_config_dict(graphic):
    try:
        with open(
            os.path.join(current_app.config[CONFIG_FILE_FOLDER], graphic), "r"
        ) as fout:
            graphic_dict_json = fout.read()
    except (OSError, IOError):
        graphic_dict_json = "{}"
    return graphic_dict_json


def sanitize_string(the_string):
    pattern = re.compile(r"\W+", re.UNICODE)
    return (pattern.sub("", the_string.replace(" ", "_"))).lower()


def invert_dict_lists(dict_to_invert):
    return {v: k for k, value_list in dict_to_invert.items() for v in value_list}


def graphic_dict_to_graphic_component_dict(graphic_dict):
    """
    change a graphic dictionary to components to be used by wizard ui
    which uses four separate forms.
    :param graphic_dict:
    :return:
    """
    graphic_dict_copy = copy.deepcopy(graphic_dict)
    component_dict = {}
    for ui_name, schema_name in UI_SCHEMA_PAIRS.items():
        component_dict[ui_name] = graphic_dict_copy.pop(schema_name, None)
    component_dict[GRAPHIC_META_INFO] = graphic_dict_copy

    return component_dict


def graphic_component_dict_to_graphic_dict(graphic_component_dict):
    """
    change the four dictionaries received from wizard ui into one graphic dictionary
    :param graphic_component_dict:
    :return:
    """
    graphic_dict = graphic_component_dict[GRAPHIC_META_INFO]
    if (
        ADDITIONAL_DATA_SOURCES in graphic_dict[DATA_SOURCES]
        and not graphic_dict[DATA_SOURCES][ADDITIONAL_DATA_SOURCES]
    ):
        del graphic_dict[DATA_SOURCES][ADDITIONAL_DATA_SOURCES]

    for ui_name, schema_name in UI_SCHEMA_PAIRS.items():
        ui_dict = graphic_component_dict.get(ui_name, {})
        if ui_dict:
            graphic_dict[schema_name] = ui_dict
    return graphic_dict


def get_layout_for_dashboard(available_pages_list):
    """
    Makes the dictionary that determines the dashboard layout page.
    Displays the graphic title to represent the graphic.
    :param available_pages_list:
    :return:
    """
    available_pages_list_copy = copy.deepcopy(available_pages_list)
    for available_page_dict in available_pages_list_copy:
        graphic_list = available_page_dict[GRAPHIC_CONFIG_FILES]
        for graphic_index, graphic_path in enumerate(graphic_list):
            graphic_json = json.loads(load_graphic_config_dict(graphic_path))
            graphic_list[graphic_index] = {
                GRAPHIC_PATH: graphic_path,
                GRAPHIC_TITLE: graphic_json[GRAPHIC_TITLE],
            }
    return available_pages_list_copy


def extract_data_sources_from_config(graphic_config):
    """
    parses out the data source names from the graph definition
    :param graphic_config:
    :return:
    """
    if DATA_SOURCES in graphic_config:
        data_source_dict = graphic_config[DATA_SOURCES]
        data_sources = {data_source_dict[MAIN_DATA_SOURCE].get(DATA_SOURCE_TYPE)}
        additional_data_source_list = data_source_dict.get(ADDITIONAL_DATA_SOURCES, [])
        for additional_data_source_dict in additional_data_source_list:
            data_sources.add(additional_data_source_dict.get(DATA_SOURCE_TYPE))
        return list(data_sources)
    else:
        return []


def copy_data_from_form_to_config(main_config, form):
    """
    copies information from the form into the main config
    :param main_config:
    :param form:
    :return:
    """
    for key in [SITE_TITLE, SITE_DESC, DATA_BACKEND]:
        main_config[key] = form[key]


def make_page_dict_for_main_config(webpage_label, page_urls):
    """
    Helper function for adding or renaming a page
    :param webpage_label:
    :param page_urls:
    :return:
    """
    candidate_url = sanitize_string(
        webpage_label
    )  # sanitizing the string so it is valid url
    if candidate_url in page_urls:
        i = 0
        while f"{candidate_url}_{i}" in page_urls:
            i += 1
        candidate_url = f"{candidate_url}_{i}"

    page_dict = {
        WEBPAGE_LABEL: webpage_label,
        URL_ENDPOINT: candidate_url,
        GRAPHIC_CONFIG_FILES: [],
    }
    return page_dict
