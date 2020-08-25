# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from datetime import datetime
import glob
import os

from flask import current_app
import pandas as pd
from pathvalidate import sanitize_filename
from werkzeug.utils import secure_filename

from database.data_handler import DataHandler
from database.utils import local_csv_handler_filter_operation
from utility.constants import (
    OPTION_COL,
    DATA_SOURCE_TYPE,
    DATA_LOCATION,
    JOIN_KEYS,
    TABLE_COLUMN_SEPARATOR,
    UNFILTERED_SELECTOR,
    COLUMN_NAME,
    ADDITIONAL_DATA_SOURCES,
    MAIN_DATA_SOURCE,
    CONFIG_FILE_FOLDER,
    DATA,
    SELECTED,
)


class LocalCSVHandler(DataHandler):
    def __init__(self, data_sources):
        """
        :param data_sources: dict defining data files and join rules
        e.g., {MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "file_type_a"},
                ADDITIONAL_DATA_SOURCES: [{DATA_SOURCE_TYPE: "file_type_b",
        JOIN_KEYS: [("column_foo_in_file_type_a", "column_bar_in_file_type_b"),
        (..., ...)]]
        """
        self.data_sources = data_sources
        self.data_file_directory = os.path.join(
            current_app.config[CONFIG_FILE_FOLDER], DATA
        )
        data_sources = [self.data_sources[MAIN_DATA_SOURCE]] + self.data_sources.get(
            ADDITIONAL_DATA_SOURCES, []
        )

        for data_source in data_sources:
            filepaths_list = self.assemble_list_of_active_data_source_csvs(data_source)
            data_source.update({DATA_LOCATION: filepaths_list})
        self.combined_data_table = self.build_combined_data_table()

    def assemble_list_of_active_data_source_csvs(self, data_source):
        data_source_name = data_source[DATA_SOURCE_TYPE]
        data_source_subfolder = os.path.join(self.data_file_directory, data_source_name)
        filepaths_list = glob.glob(f"{data_source_subfolder}/*.csv")
        if data_source_name in current_app.config.active_data_source_filters:
            filepaths_list = current_app.config.active_data_source_filters[
                data_source_name
            ]
        assert len(filepaths_list) > 0
        return filepaths_list

    @staticmethod
    def build_df_for_data_source_type(data_source):
        # There may be multiple files for a particular data source type
        data_source_df = pd.concat(
            [pd.read_csv(filepath) for filepath in data_source[DATA_LOCATION]]
        )
        # add the data_source/table name as a prefix to disambiguate columns
        data_source_df = data_source_df.add_prefix(
            f"{data_source[DATA_SOURCE_TYPE]}{TABLE_COLUMN_SEPARATOR}"
        )
        return data_source_df

    def build_combined_data_table(self):
        """
        Uses list of data sources to build a joined dataframe connecting related data
        todo: this is not likely changing very often, and may be slow to load
        Consider caching the data on a persistent LocalCSVHandler object instead of loading csvs and  merging every time we access the data
        :return: combined_data_table dataframe
        """
        combined_data_table = self.build_df_for_data_source_type(
            self.data_sources[MAIN_DATA_SOURCE]
        )
        for data_source in self.data_sources.get(ADDITIONAL_DATA_SOURCES, []):
            data_source_df = self.build_df_for_data_source_type(data_source)
            left_keys, right_keys = zip(*data_source[JOIN_KEYS])
            # left join the next data source to our combined data table
            combined_data_table = combined_data_table.merge(
                data_source_df, how="left", left_on=left_keys, right_on=right_keys,
            )
        return combined_data_table

    def get_column_data(self, cols: list, filters: list = None) -> dict:
        # error checking would be good
        """
        :param cols:
        :param filters:
        :return:
        """
        if filters is None:
            filters = []
        cols_for_filters = [filter_dict[OPTION_COL] for filter_dict in filters]
        all_to_include_cols = set(cols + list(cols_for_filters))
        df = self.combined_data_table[all_to_include_cols]
        for filter_dict in filters:
            column = df[filter_dict[OPTION_COL]]
            df = df[local_csv_handler_filter_operation(column, filter_dict)]

        return df[cols]

    def get_column_unique_entries(self, cols: list, filters: list = None) -> dict:
        if filters is None:
            filters = []
        df = self.combined_data_table.copy(deep=False)
        for filter_dict in filters:
            if not filter_dict[SELECTED]:
                # No filter has been applied
                continue
            column = df[filter_dict[OPTION_COL]]
            df = df[local_csv_handler_filter_operation(column, filter_dict)]

        unique_dict = {}
        for col in cols:
            if any(
                [
                    (filter_[COLUMN_NAME] == col and filter_.get(UNFILTERED_SELECTOR))
                    for filter_ in filters
                ]
            ):
                # if this column matches one in the filters dict that is listed as an
                # UNFILTERED_SELECTOR, don't apply an subsetting on the unique values
                table = self.combined_data_table
            else:
                table = df
            # entry == entry is a shortcut to remove None and NaN values

            unique_dict[col] = [
                str(entry) for entry in table[col].unique() if entry == entry
            ]
        return unique_dict


class LocalCSVDataInventory(LocalCSVHandler):
    def __init__(self, data_sources):
        # Instance methods for this class refer to single data source table
        assert len(data_sources) == 1
        self.data_source_name = data_sources[MAIN_DATA_SOURCE][DATA_SOURCE_TYPE]

    @staticmethod
    def get_available_data_sources():
        return [
            f.name
            for f in os.scandir(
                os.path.join(current_app.config[CONFIG_FILE_FOLDER], DATA)
            )
            if f.is_dir()
        ]

    def get_identifiers_for_data_source(self):
        full_path = os.path.join(
            current_app.config[CONFIG_FILE_FOLDER], DATA, self.data_source_name,
        )
        list_of_files = glob.glob(f"{full_path}/*.csv")
        assert len(list_of_files) > 0
        return list_of_files

    def get_schema_for_data_source(self):
        list_of_files = self.get_identifiers_for_data_source()
        latest_filepath = max(list_of_files, key=os.path.getctime)
        return pd.read_csv(latest_filepath, nrows=1).columns.tolist()

    def write_data_upload_to_backend(self, uploaded_data_df, file_name=None):
        """
        :param file_name:
        :param uploaded_data_df: pandas dataframe on which we have already done validation
        :param data_source_name:

        :return: Empty list representing columns not in the new file that are in the old. INcluded for function signature matching
        """

        file_name = (
            datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            if (file_name is None)
            else sanitize_filename(secure_filename(file_name))
        )
        file_name = (
            file_name if file_name.endswith(".csv") else "".join([file_name, ".csv"])
        )

        file_path = os.path.join(
            current_app.config[CONFIG_FILE_FOLDER],
            DATA,
            self.data_source_name,
            file_name,
        )
        uploaded_data_df.to_csv(file_path)
        return []
