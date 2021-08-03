# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from abc import ABC, abstractmethod


class DataHandler(ABC):
    def __init__(
        self,
        data_sources: dict,
        selectable_data_dict: dict = None,
        addendum_dict: dict = None,
        only_use_active: bool = True,
    ):
        """
        :param only_use_active: filters the query based on the "active" value
        in the upload_metadata table for each upload
        :param data_sources: a dictionary that matches the schemas returned by build_data_sources_schema in the
         DataConfigInterfaceBuilder class
        """
        self.data_sources = data_sources
        self.only_use_active = only_use_active
        if selectable_data_dict is None:
            selectable_data_dict = {}
        if addendum_dict is None:
            addendum_dict = {}
        self.selectable_data_dict = selectable_data_dict
        self.addendum_dict = addendum_dict
        self.unique_entry_dict = {}

        self.select_info = []

    @abstractmethod
    def get_column_data(self, cols: set, orient: str = "list"):
        """
        :param cols: set of column names, including all columns for which data should be returned
        :param orient: format for key-value pairs
        see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html
        The graphics class specifies the data in different formats. Currently implement *list* (used by most graphics
        class) and *records* (used by bootstrap table)
        :return: a dict or list depending on the orient parameter

        """
        pass

    def get_column_names_for_data_source(self):
        """
        This function can but does not need to be implemented in the child classes
        :return: list of column names
        """
        return []

    def get_column_unique_entries(self, cols: set) -> dict:
        """
        :param cols: set of column names
        :return: A dict keyed by column names and valued with a list unique values in that column as strings
        """
        return {}

    def get_column_unique_entries_based_on_type(self, cols: set) -> (dict, dict):
        """
        :param cols: set of column names
        :return: dict1 - A dict keyed by column names and valued with the unique values in that column for columns that
        will be used for equality filtering
        :return: dict2 - A dict keyed by different types of columns
         (numerical, catagorical etc.) to be used by the schema.
        """
        return {}, {}

    def add_instructions_to_config_dict(self):
        pass

    def create_data_subselect_info_for_plot(self):
        pass
