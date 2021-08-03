# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0


from abc import ABC, abstractmethod

from utility.constants import LIST


class Graphic(ABC):
    def __init__(
        self, plot_specific_info: dict, addendum_dict: dict = None,
    ):

        """
        :param plot_specific_info: dictionary that contains the settings for the plot.
        """
        self.plot_specific_info = plot_specific_info
        self.data = {}
        self.graph_json_str = "{}"

        if addendum_dict is None:
            addendum_dict = {}

        self.addendum_dict = addendum_dict
        self.select_info = []

    @staticmethod
    @abstractmethod
    def get_graph_html_template() -> str:
        """
        returns the graph html template the graphic library uses
        """
        raise NotImplementedError

    @abstractmethod
    def make_dict_for_html_plot(self):
        """
        creates the json that is passed to the html template
        """
        raise NotImplementedError

    @abstractmethod
    def get_data_columns(self) -> set:
        """
        extracts what columns of data are needed from the database
        :return:
        """
        raise NotImplementedError

    def get_data_orient(self) -> str:
        """
        The type of the key-value pairs the data is in see
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html
        """
        return LIST

    def add_instructions_to_config_dict(self):
        """
        OPTIONAL
        Implement this function for interactive data selectors.
        Uses the addendum_dict to modify plot_specific_info
        :return:
        """
        pass

    def create_data_subselect_info_for_plot(self):
        """
        OPTIONAL
        Implement this function for interactive data selectors.
        Creates select_info list for data selectors on the dashboard. See plotly_plot for example
        :return:
        """
        pass
