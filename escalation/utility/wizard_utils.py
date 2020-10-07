import copy
import json
import os
import re

from flask import current_app

from utility.constants import *

UI_SCHEMA_PAIRS = {
    VISUALIZATION: VISUALIZATION_OPTIONS,
    SELECTOR: SELECTABLE_DATA_DICT,
    PLOTLY: PLOT_SPECIFIC_INFO,
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

    visualization_components = {HOVER_DATA: {}, GROUPBY: {}, AGGREGATE: {}}
    selector_components = {FILTER: [], NUMERICAL_FILTER: [], AXIS: [], GROUPBY: []}

    # add in missing elements so the options show up in the json editor
    component_dict[GRAPHIC_META_INFO][DATA_SOURCES][
        ADDITIONAL_DATA_SOURCES
    ] = component_dict[GRAPHIC_META_INFO][DATA_SOURCES].get(ADDITIONAL_DATA_SOURCES, [])

    for component, empty_element in visualization_components.items():
        component_dict[VISUALIZATION][component] = component_dict[VISUALIZATION].get(
            component, empty_element
        )
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

    graphic_dict[PLOT_SPECIFIC_INFO] = graphic_component_dict[PLOTLY]

    visualization_dict = prune_visualization_dict(graphic_component_dict[VISUALIZATION])
    if visualization_dict:
        graphic_dict[VISUALIZATION_OPTIONS] = visualization_dict

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
        HOVER_DATA: [VISUALIZATION_OPTIONS, HOVER_DATA],
        GROUPBY: [VISUALIZATION_OPTIONS, GROUPBY],
        AGGREGATE: [VISUALIZATION_OPTIONS, AGGREGATE],
        FILTER: [SELECTABLE_DATA_DICT, FILTER],
        NUMERICAL_FILTER: [SELECTABLE_DATA_DICT, NUMERICAL_FILTER],
        AXIS: [SELECTABLE_DATA_DICT, AXIS],
        GROUPBY_SELECTOR: [SELECTABLE_DATA_DICT, GROUPBY],
    }
    FIRST_LEVEL_COLLAPSE = {
        VISUALIZATION_OPTIONS: [HOVER_DATA, GROUPBY, AGGREGATE],
        SELECTABLE_DATA_DICT: [FILTER, NUMERICAL_FILTER, AXIS, GROUPBY],
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
        VISUALIZATION_OPTIONS,
        ADDITIONAL_DATA_SOURCES,
        HOVER_DATA,
        GROUPBY,
        AGGREGATE,
        FILTER,
        NUMERICAL_FILTER,
        AXIS,
        GROUPBY_SELECTOR,
    ]
    return dict.fromkeys(keys, True)


def prune_visualization_dict(visualization_dict):
    """
    Get rid of empty entries in visualization dict
    :param visualization_dict:
    :return:
    """
    new_visualization_dict = {}
    # when the form is left blank the entries of visualization_dict have
    # COLUMN_NAME key that points to an empty list
    for vis_key, vis_dict in visualization_dict.items():
        if vis_dict.get(COLUMN_NAME):
            new_visualization_dict[vis_key] = vis_dict
    return new_visualization_dict


def prune_selector_dict(selector_dict):
    """
    Get rid of empty entries in selector dict
    :param selector_dict:
    :return:
    """
    new_selector_dict = {}
    for sel_key, sel_info in selector_dict.items():
        if (sel_key == GROUPBY and sel_info.get(ENTRIES)) or (
            sel_key != GROUPBY and sel_info
        ):
            new_selector_dict[sel_key] = sel_info
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


def get_possible_column_names_and_values(
    data_source_names, data_handler_class, get_unique_values=True
):
    """
    Used to populate a dropdown in the config wizard with any column from the data
    sources included in a figure, unique_entries used to populate default selected.
    :param data_source_names: list of data source name strings
    :param data_handler_class: backend-specific data inventory class
    :return: possible_column_names list, unique_entries dict.
    :param get_unique_values: if true calculates unique values for each column
    """
    possible_column_names = []
    unique_entries = {}
    for data_source_name in data_source_names:
        data_inventory = data_handler_class(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source_name}}
        )
        column_names_for_data_source = data_inventory.get_schema_for_data_source()
        possible_column_names.extend(column_names_for_data_source)
        if get_unique_values:
            unique_entries_for_data_source = data_inventory.get_column_unique_entries(
                column_names_for_data_source
            )
            unique_entries.update(unique_entries_for_data_source)
    return possible_column_names, unique_entries


def get_data_source_info(active_data_source_names=None):
    """
    gets the available data sources and the possible column names based on the data source in the config
    :param active_data_source_names: list of data source name strings
    :return:
    """
    if active_data_source_names is None:
        active_data_source_names = []
    data_inventory_class = current_app.config.data_backend_writer
    data_source_names = data_inventory_class.get_available_data_sources()
    active_data_source_names = [
        data_source_name
        for data_source_name in active_data_source_names
        if data_source_name in data_source_names
    ]
    if data_source_names and not active_data_source_names:
        # default to the first in alphabetical order
        active_data_source_names = [min(data_source_names)]
    possible_column_names, unique_entries = get_possible_column_names_and_values(
        active_data_source_names, current_app.config.data_handler
    )
    return data_source_names, possible_column_names, unique_entries


def extract_data_sources_from_config(graphic_config):
    """
    parses out the data source names from the graph definition
    :param graphic_config:
    :return:
    """
    if DATA_SOURCES in graphic_config:
        data_source_dict = graphic_config[DATA_SOURCES]
        data_sources = set([data_source_dict[MAIN_DATA_SOURCE].get(DATA_SOURCE_TYPE)])
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
