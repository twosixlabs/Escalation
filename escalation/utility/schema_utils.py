import itertools

from flask import current_app

from utility.constants import MAIN_DATA_SOURCE, DATA_SOURCE_TYPE


class SchemaDataHolder:
    def __init__(self, active_data_source_names=None):
        if active_data_source_names is None:
            self.active_data_source_names = []
        else:
            self.active_data_source_names = active_data_source_names
        # set by get_data_source_info
        self.data_source_names = None
        # set by get_possible_column_names_and_values called by get_data_source_info
        # todo: rename as data_source_column_names?
        self.possible_column_names = None
        self.unique_entries_dict = None
        self.filter_dict = None
        self.unique_entry_values_list = None

    def sort_data(self):
        for info_list in [
            self.data_source_names,
            self.possible_column_names,
            self.unique_entry_values_list,
        ]:
            if info_list:
                info_list.sort()
        for info_list in self.filter_dict.values():
            if info_list:
                info_list.sort()

    def set_possible_column_names_and_unique_values(self, get_unique_values=True):
        """
        Used to populate a dropdown in the config wizard with any column from the data
        sources included in a figure, unique_entries used to populate default selected.
        :param get_unique_values: if true calculates unique values for each column
        """
        (
            self.possible_column_names,
            self.unique_entries_dict,
            self.filter_dict,
        ) = get_possible_column_names_and_values(
            self.active_data_source_names, get_unique_values=get_unique_values
        )
        self.unique_entry_values_list = self.get_unique_entries_as_single_list()

    def get_data_source_info(self):
        """
        gets the available data sources and the possible column names based on the data source in the config
        :return:
        """
        self.data_source_names = get_data_sources()
        self.active_data_source_names = [
            data_source_name
            for data_source_name in self.active_data_source_names
            if data_source_name in self.data_source_names
        ]
        if self.data_source_names and not self.active_data_source_names:
            # default to the first in alphabetical order
            self.active_data_source_names = [min(self.data_source_names)]

        self.set_possible_column_names_and_unique_values()

    def get_unique_entries_as_single_list(self):
        # concatenating into one large list with no duplicates
        unique_entries_list = list(
            set(itertools.chain.from_iterable(self.unique_entries_dict.values()))
        )
        return unique_entries_list


def conditional_dict(key, value, extra=None):
    """
    Return key value pair when value is truthy otherwise returns empty dict
    """
    return (
        {key: (value + extra) if extra else value, "format": "select2"} if value else {}
    )


def get_data_sources():
    data_inventory_class = current_app.config.data_backend_writer
    data_sources = data_inventory_class.get_available_data_sources()
    return data_sources


def get_data_sources_and_column_names():
    """
    used for populating the data source schema in the wizard landing page
    :return:
    """
    data_sources = get_data_sources()
    possible_column_names, _, _ = get_possible_column_names_and_values(
        data_sources, get_unique_values=False
    )
    return data_sources, possible_column_names


def get_possible_column_names_and_values(data_sources, get_unique_values=True):
    """
    Used to populate a dropdown in the config wizard with any column from the data
    sources included in a figure, unique_entries used to populate default selected.
    :param data_source_names: list of data source name strings
    :param get_types: if true calculates the type of each column
    :param get_unique_values: if true calculates unique values for each column
    """
    possible_column_names = []
    unique_entries = {}
    filter_dict = {}
    data_handler_class = current_app.config.data_handler
    for i, data_source_name in enumerate(data_sources):
        data_handler_instance = data_handler_class(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source_name}}
        )
        column_names_for_data_source = (
            data_handler_instance.get_column_names_for_data_source()
        )

        possible_column_names.extend(column_names_for_data_source)
        if get_unique_values:
            if i == 0:
                (
                    unique_entries,
                    filter_dict,
                ) = data_handler_instance.get_column_unique_entries_based_on_type(
                    column_names_for_data_source
                )
            else:
                (
                    unique_entries_for_data_source,
                    filter_dict_for_data_source,
                ) = data_handler_instance.get_column_unique_entries_based_on_type(
                    column_names_for_data_source
                )
                unique_entries.update(unique_entries_for_data_source)
                for key in filter_dict:
                    filter_dict[key].extend(filter_dict_for_data_source[key])
    return possible_column_names, unique_entries, filter_dict
