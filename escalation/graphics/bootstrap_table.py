# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import copy
import json
import plotly
from flask import render_template
from graphics.graphic_plot import Graphic
from utility.constants import DATA, COLUMNS, FIELD, TITLE, FORMATTER, RECORDS


class BootstrapTable(Graphic):
    def make_dict_for_html_plot(self):
        """
        Makes the dictionary that bootstrap_table.html takes in.
        layout options for bootstrap_table are currently not implemented.
        based on https://bootstrap-table.com/
        :return:
        """
        plot_options = self.plot_specific_info
        col_list = plot_options[COLUMNS]
        for col_dict in col_list:
            if col_dict.get(TITLE, None):
                continue
            col_dict[TITLE] = col_dict[FIELD]
        plot_options[DATA] = self.data

        self.graph_json_str = json.dumps(plot_options)

    @staticmethod
    def get_graph_html_template() -> str:
        return "bootstrap-table.html"

    def get_data_columns(self) -> set:
        """
        extracts what columns of data are needed from the plot_options
        :param plot_options:
        :return:
        """
        set_of_column_names = {
            col_obj[FIELD] for col_obj in self.plot_specific_info[COLUMNS]
        }
        return set_of_column_names

    def get_data_orient(self) -> str:
        """
        The type of the key-value pairs the data is in see
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html
        """
        return RECORDS
