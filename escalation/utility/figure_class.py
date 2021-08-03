from collections import defaultdict

from flask import current_app

from graphics.available_graphics import AVAILABLE_GRAPHICS
from utility.constants import *

DEFAULT_VISUALIZATION_OPTIONS = {
    HEIGHT: 400,
    # Currently, the width is determined by the aspect ratio
}


class Figure:
    def __init__(
        self, figure_name: str, graphic_config_dict: dict, addendum_dict: dict = None
    ):

        """
        We build a page based on 2 dictonaries, what is in the config and what is submitted in the HTML form.
        :param figure_name: string identifier for the corresponding figure.
        :param graphic_config_dict: Copy of part of the original config dict.
        Outside of getting the data, only functions in reformatting_functions.py should modifies the copy of config dict.
        :param addendum_dict: e.g ImmutableMultiDict([('graphic_name', 'graphic_0'), ('selection_0', 'SHOW_ALL_ROW'),
         ('selection_2_upper_operation', '<='), ('selection_2_upper_value', '4'))])
        Should not pass an empty ImmutableMultiDict
        """
        self.figure_name = figure_name
        if addendum_dict is None:
            addendum_dict = {}
        self.graphic_dict = graphic_config_dict
        self.addendum_dict = addendum_dict
        graphic_class = AVAILABLE_GRAPHICS[graphic_config_dict[PLOT_MANAGER]][
            GRAPHICS_CLASS
        ]
        self.graphic_object = graphic_class(
            graphic_config_dict[PLOT_SPECIFIC_INFO], addendum_dict
        )
        self.plot_data_handler = current_app.config.data_handler(
            graphic_config_dict[DATA_SOURCES],
            graphic_config_dict.get(SELECTABLE_DATA_DICT, {}),
            addendum_dict,
        )
        self.visualization_dict = DEFAULT_VISUALIZATION_OPTIONS

    def make_html_dict(self):

        self.plot_data_handler.add_instructions_to_config_dict()
        self.graphic_object.add_instructions_to_config_dict()

        plot_data = self.plot_data_handler.get_column_data(
            self.graphic_object.get_data_columns(),
            self.graphic_object.get_data_orient(),
        )
        # makes a json file as required by js plotting documentation
        self.graphic_object.data = plot_data
        self.graphic_object.make_dict_for_html_plot()
        self.plot_data_handler.create_data_subselect_info_for_plot()
        self.graphic_object.create_data_subselect_info_for_plot()
        select_info = (
            self.plot_data_handler.select_info + self.graphic_object.select_info
        )
        self.visualization_dict.update(self.graphic_dict.get(VISUALIZATION_OPTIONS, {}))

        html_dict = {
            JINJA_GRAPH_HTML_FILE: self.graphic_object.get_graph_html_template(),
            JINJA_SELECT_INFO: select_info,
            GRAPHIC_TITLE: self.graphic_dict.get(GRAPHIC_TITLE, self.figure_name),
            GRAPHIC_DESC: self.graphic_dict.get(GRAPHIC_DESC, ""),
            JINJA_PLOT_INFO: self.graphic_object.graph_json_str,
            PLOT_ID: self.figure_name,
            VISUALIZATION_OPTIONS: self.visualization_dict,
        }

        return html_dict
