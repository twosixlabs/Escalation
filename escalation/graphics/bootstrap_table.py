# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy
import json
import plotly
from flask import render_template
from graphics.graphic_class import Graphic
from utility.constants import COLUMN_NAME, DATA, LAYOUT, OPTIONS

HEADER_INFO = "header_info"


def remove_duplicate_column_names(list_of_dict_of_header_info):
    """
    No two columns of the table can have the same data
    :param plot_options:
    :return:
    """
    list_of_column_names = []
    list_of_dict_of_header_info_copy = copy.deepcopy(list_of_dict_of_header_info)
    for index, dict_of_header_info in enumerate(list_of_dict_of_header_info_copy):
        column = dict_of_header_info[COLUMN_NAME]
        if column in list_of_column_names:
            del list_of_dict_of_header_info[index]
        else:
            list_of_column_names.append(column)
    return list_of_column_names, list_of_dict_of_header_info


class BootstrapTable(Graphic):
    @staticmethod
    def make_dict_for_html_plot(data, plot_options, visualization_options=None):
        """
        Makes the dictionary that bootstrap_table.html takes in.
        layout options for bootstrap_table are currently not implemented.
        based on https://bootstrap-table.com/
        :param data: a pandas dataframe
        :param plot_options:
        :param visualization_options: not used
        :return:
        """
        list_of_column_names = remove_duplicate_column_names(plot_options[DATA])
        table_dict = {
            HEADER_INFO: plot_options[DATA],
            DATA: json.dumps(data[list_of_column_names].to_dict("records")),
            OPTIONS: plot_options.get(OPTIONS, {}),
        }
        return table_dict

    @staticmethod
    def get_data_columns(plot_options) -> set:
        """
        extracts what columns of data are needed from the plot_options
        :param plot_options:
        :return:
        """
        set_of_column_names = set()
        for dict_of_data_for_each_column in plot_options[DATA]:
            set_of_column_names.add(dict_of_data_for_each_column[COLUMN_NAME])
        return set_of_column_names
