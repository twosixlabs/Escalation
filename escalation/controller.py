# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import copy
import json
import os

from flask import current_app

from database.data_handler import DataHandler
from graphics.utils.available_graphics import AVAILABLE_GRAPHICS
from utility.constants import *


def get_data_for_page(single_page_config_dict: dict, addendum_dict=None) -> list:
    """

    :param single_page_config_dict: A dictionary containing all the information from the config json file
    :param addendum_dict: json received from post. # todo: describe how this form is structured, and how we restructure it in reformat_html_form_dict
    :return: dictionary to be read by jinja to build the page
    """

    single_page_config_dict = copy.deepcopy(single_page_config_dict)
    graphic_object_dict = make_dict_of_graphic_objects(
        single_page_config_dict, addendum_dict
    )
    plot_specs = assemble_html_with_graphs_from_page_config(graphic_object_dict)

    return plot_specs


def make_dict_of_graphic_objects(
    single_page_graphic_config_dict: dict, addendum_dict: dict = None
) -> dict:
    """
    We build a page based on 2 dictonaries, what is in the config and what is submitted in the HTML form.
    :param single_page_graphic_config_dict: Copy of part of the original config dict.
    :param addendum_dict: e.g ImmutableMultiDict([('graphic_name', 'graphic_0'), ('selection_0', 'SHOW_ALL_ROW'),
     ('selection_2_upper_operation', '<='), ('selection_2_upper_value', '4'))])
    Should not pass an empty ImmutableMultiDict
    :return: dictionary of Graphic classes
    """
    if addendum_dict is None:
        addendum_dict = {}
    graphic_object_dict = {}
    for graphic_name, graphic_dict in single_page_graphic_config_dict.items():
        graphic_class = AVAILABLE_GRAPHICS[graphic_dict[PLOT_MANAGER]][OBJECT]
        graphic_object = graphic_class(
            graphic_dict, addendum_dict.get(graphic_name, {})
        )
        graphic_object.add_instructions_to_config_dict()
        graphic_object_dict[graphic_name] = graphic_object
    return graphic_object_dict


def assemble_html_with_graphs_from_page_config(graphic_object_dict: dict) -> list:
    """
    creates dictionary to be read in by the html file to plot the graphics and selectors
    :param plot_list:
    :param filter_dict:
    :param axes_to_show_per_plot: keyed by html_id of plot, value is dict with some of xyz keys and valued by column name
    :return:
    """
    plot_specs = []

    for plot_key, graphic_object in graphic_object_dict.items():
        plot_data_handler = current_app.config.data_handler(
            graphic_object.graphic_dict[DATA_SOURCES]
        )

        data_filters = graphic_object.graphic_dict.get(DATA_FILTERS, [])
        plot_data = plot_data_handler.get_column_data(
            graphic_object.get_data_columns(), data_filters,
        )
        # makes a json file as required by js plotting documentation
        graphic_object.data = plot_data
        graphic_object.make_dict_for_html_plot()

        unique_entry_dict = plot_data_handler.get_column_unique_entries(
            graphic_object.get_columns_that_need_unique_entries(), filters=data_filters
        )
        graphic_object.unique_entry_dict = unique_entry_dict
        graphic_object.create_data_subselect_info_for_plot()

        html_dict = {
            JINJA_GRAPH_HTML_FILE: graphic_object.get_graph_html_template(),
            JINJA_SELECT_INFO: graphic_object.select_info,
            GRAPHIC_TITLE: graphic_object.graphic_dict.get(GRAPHIC_TITLE, plot_key),
            GRAPHIC_DESC: graphic_object.graphic_dict.get(GRAPHIC_DESC, ""),
            JINJA_PLOT_INFO: graphic_object.graph_json_str,
            PLOT_ID: plot_key,
        }
        plot_specs.append(html_dict)
    return plot_specs


def create_labels_for_available_pages(available_pages_list: list) -> list:
    """
    Reformats a list of dashboard pages from the main app config json for template
    :param available_pages_list:
    :return: list of dicts defining hyperlink text and url for navbar
    """
    labels = []
    for available_page in available_pages_list:
        labels.append(
            {
                WEBPAGE_LABEL: available_page[WEBPAGE_LABEL],
                LINK: available_page[URL_ENDPOINT],
            }
        )
    return labels


def make_pages_dict(available_pages_list, config_file_folder) -> dict:
    """
    Pulls in all the config files referenced in the main config to make a large dictionary.
    :param config_file_folder:
    :param available_pages_list:
    :return:
    """
    available_pages_dict = {}
    for page in available_pages_list:
        page_dict = {}
        for graphic_config_file_path in page[GRAPHIC_CONFIG_FILES]:
            with open(
                os.path.join(config_file_folder, graphic_config_file_path), "r"
            ) as config_file:
                config_dict = json.load(config_file)
            graphic_key = os.path.splitext(os.path.basename(graphic_config_file_path))[
                0
            ]
            page_dict[graphic_key] = config_dict
        available_pages_dict[page[URL_ENDPOINT]] = page_dict
    return available_pages_dict


def get_datasource_metadata_formatted_for_admin_panel():
    """
    Gets meta data for admin and download page.
    Formats a dictionary keyed with datasource, valued with a dict defining upload ids
    and their corresponding upload metadata.
    This dict is formatted to be read by bootstrap-table
    """
    data_inventory = current_app.config.data_backend_writer
    existing_data_sources = data_inventory.get_available_data_sources()
    data_sources = sorted(existing_data_sources)
    data_source_dict = data_inventory.get_data_upload_metadata(data_sources)
    # this allows the dictionary to work with bootstrap-table with html form as a post request.
    data_source_dict = {
        data_source: {
            "ids": [element[UPLOAD_ID] for element in identifiers_metadata_dict_list],
            "data": json.dumps(identifiers_metadata_dict_list),
        }
        for data_source, identifiers_metadata_dict_list in data_source_dict.items()
    }
    return data_source_dict
