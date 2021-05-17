import copy
import json
import os
import re

from flask import current_app

from utility.constants import *

UI_SCHEMA_PAIRS = {
    SELECTOR: SELECTABLE_DATA_DICT,
    GRAPHIC: PLOT_SPECIFIC_INFO,
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
        component_dict[ui_name] = graphic_dict_copy.pop(schema_name, {})
    component_dict[GRAPHIC_META_INFO] = graphic_dict_copy

    selector_components = {FILTER: [], NUMERICAL_FILTER: [], GROUPBY: []}

    # add in missing elements so the options show up in the json editor
    component_dict[GRAPHIC_META_INFO][DATA_SOURCES][
        ADDITIONAL_DATA_SOURCES
    ] = component_dict[GRAPHIC_META_INFO][DATA_SOURCES].get(ADDITIONAL_DATA_SOURCES, [])

    for component, empty_element in selector_components.items():
        component_dict[SELECTOR][component] = component_dict[SELECTOR].get(
            component, empty_element
        )

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

    graphic_dict[PLOT_SPECIFIC_INFO] = graphic_component_dict[GRAPHIC]

    selector_dict = prune_selector_dict(graphic_component_dict[SELECTOR])
    if selector_dict:
        graphic_dict[SELECTABLE_DATA_DICT] = selector_dict

    return graphic_dict


def generate_collapse_dict_from_graphic_component_dict(graphic_dict):
    """
    Makes a dictionary for the ui wizard which elements should be collapsed (True)/ not collapsed (False)
    :param graphic_dict:
    :return:
    """
    HIGH_LEVEL_COLLAPSE = {
        ADDITIONAL_DATA_SOURCES: [DATA_SOURCES, ADDITIONAL_DATA_SOURCES],
        FILTER: [SELECTABLE_DATA_DICT, FILTER],
        NUMERICAL_FILTER: [SELECTABLE_DATA_DICT, NUMERICAL_FILTER],
        GROUPBY_SELECTOR: [SELECTABLE_DATA_DICT, GROUPBY],
    }
    FIRST_LEVEL_COLLAPSE = {
        SELECTABLE_DATA_DICT: [FILTER, NUMERICAL_FILTER, GROUPBY_SELECTOR],
    }

    collapse_dict = {}
    for key, path in HIGH_LEVEL_COLLAPSE.items():
        collapse_dict[key] = (
            False if graphic_dict.get(path[0], {}).get(path[1]) else True
        )

    for key, dependant_elements in FIRST_LEVEL_COLLAPSE.items():
        collapse_dict[key] = all([collapse_dict[item] for item in dependant_elements])

    return collapse_dict


def get_default_collapse_dict():
    """
    collapse dict for a new graphic
    :return:
    """
    keys = [
        SELECTABLE_DATA_DICT,
        ADDITIONAL_DATA_SOURCES,
        FILTER,
        NUMERICAL_FILTER,
        GROUPBY_SELECTOR,
    ]
    return dict.fromkeys(keys, True)


def prune_selector_dict(selector_dict):
    """
    Get rid of empty entries in selector dict
    :param selector_dict:
    :return:
    """
    new_selector_dict = {}
    for sel_key, sel_info in selector_dict.items():
        if sel_key == GROUPBY and sel_info.get(ENTRIES):
            new_selector_dict[sel_key] = sel_info
        if sel_key == FILTER and sel_info:

            new_sel_info = []
            # Getting rid empty DEFAULT_SELECTED
            for filter_dict in sel_info:
                if not filter_dict.get(DEFAULT_SELECTED, []):
                    filter_dict.pop(DEFAULT_SELECTED, None)
                new_sel_info.append(filter_dict)
            new_selector_dict[sel_key] = new_sel_info
        if sel_key == NUMERICAL_FILTER and sel_info:
            new_sel_info = []
            # Getting rid of null values in max and min
            for numerical_filter_dict in sel_info:
                for extrema in [MAX, MIN]:
                    if numerical_filter_dict.get(extrema, None) is None:
                        numerical_filter_dict.pop(extrema, None)
                new_sel_info.append(numerical_filter_dict)
                new_selector_dict[sel_key] = new_sel_info

    return new_selector_dict


def make_empty_component_dict():
    """
    makes an empty version of component dict to be used by wizard ui
    :return:
    """
    component_dict = {}
    for ui_name, schema_name in UI_SCHEMA_PAIRS.items():
        component_dict[ui_name] = {}
    component_dict[GRAPHIC_META_INFO] = {}
    return component_dict


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
