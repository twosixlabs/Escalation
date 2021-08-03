# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import copy
import json
import os

from flask import current_app
from utility.constants import *
from utility.figure_class import Figure


def get_data_for_page(single_page_config_dict: dict, addendum_dict=None) -> list:
    """
    :param single_page_config_dict: A dictionary containing all the information from the config json file
    :param addendum_dict: json received from post.
    :return: dictionary to be read by jinja to build the page
    """

    single_page_config_dict_copy = copy.deepcopy(single_page_config_dict)
    plot_specs = []

    if addendum_dict is None:
        addendum_dict = {}
    for figure_name, figure_name_dict in single_page_config_dict_copy.items():
        figure_object = Figure(
            figure_name, figure_name_dict, addendum_dict.get(figure_name, {})
        )
        plot_specs.append(figure_object.make_html_dict())

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
