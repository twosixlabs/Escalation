# Copyright [2021] [Two Six Labs, LLC],
# Licensed under the Apache License, Version 2.0,
from abc import ABC, abstractmethod

from utility.schema_utils import SchemaDataHolder


class GraphicsConfigInterfaceBuilder(ABC):
    def __init__(self, data_holder: SchemaDataHolder):
        self.data_holder = data_holder

    @abstractmethod
    def build_individual_plot_type_schema(self, plot_type):
        # must be implemented in subclass for graphic library
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_available_plots():
        """
        :return:An array of dictionaries with two keys:
        Name: shown name to the user
        Value: name of the schema, input to build_individual_plot_type_schema
        """
        raise NotImplementedError
