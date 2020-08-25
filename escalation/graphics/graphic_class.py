# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0


from abc import ABC, abstractmethod


class Graphic(ABC):
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def make_dict_for_html_plot(self, data, data_to_struct, plot_options, hover_data):
        """


        :param data: dictionary of data
        :param data_to_struct: instructions of some kind how to put the data into plot_options
        :param plot_options: dictionary that contains all the information to make a graphic minus the data
        :param hover_data:
        :return: instructions that will be passed to the html that will plot the object.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_data_columns(self, plot_options) -> set:
        """
        extracts what columns of data are needed from the plot_options
        :param plot_options:
        :return:
        """
        raise NotImplementedError
