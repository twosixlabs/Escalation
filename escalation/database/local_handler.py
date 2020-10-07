# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from collections import defaultdict, namedtuple
from datetime import datetime
import glob
import os
import shutil

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
    DATA_UPLOAD_METADATA,
    UPLOAD_ID,
    ACTIVE,
    UPLOAD_TIME,
    TABLE_NAME,
    USERNAME,
    NOTES,
    DATETIME_FORMAT,
    INDEX_COLUMN,
)
from utility.exceptions import ValidationError


class LocalCSVHandler(DataHandler):
    def __init__(self, data_sources, only_use_active: bool = True):
        """
        :param data_sources: dict defining data files and join rules
        e.g., {MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: "file_type_a"},
                ADDITIONAL_DATA_SOURCES: [{DATA_SOURCE_TYPE: "file_type_b",
        JOIN_KEYS: [("column_foo_in_file_type_a", "column_bar_in_file_type_b"),
        (..., ...)]]
        """
        self.data_sources = data_sources
        self.only_use_active = only_use_active
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

    @staticmethod
    def get_data_upload_metadata_path():
        return os.path.join(
            current_app.config[CONFIG_FILE_FOLDER],
            DATA,
            DATA_UPLOAD_METADATA,
            DATA_UPLOAD_METADATA + ".csv",
        )

    @classmethod
    def get_data_upload_metadata_df(cls):
        metadata_path = cls.get_data_upload_metadata_path()
        return pd.read_csv(metadata_path)

    @classmethod
    def filter_out_inactive_files(cls, files_list, data_source_name):
        data_upload_metadata = cls.get_data_upload_metadata_df()
        # looking for entries in the metadata that say a file is NOT active
        # lets the files default to active if added outside the app functionality
        filtered_uploads = data_upload_metadata[
            (data_upload_metadata.table_name == data_source_name)
            & (~data_upload_metadata.active)
        ][UPLOAD_ID].values
        files_list = [
            upload_id for upload_id in files_list if upload_id not in filtered_uploads
        ]
        return files_list

    def assemble_list_of_active_data_source_csvs(self, data_source):
        data_source_name = data_source[DATA_SOURCE_TYPE]
        data_source_subfolder = os.path.join(self.data_file_directory, data_source_name)
        filepaths_list = glob.glob(f"{data_source_subfolder}/*.csv")
        if self.only_use_active:
            filepaths_list = self.filter_out_inactive_files(
                filepaths_list, data_source_name,
            )
        assert len(filepaths_list) > 0
        return filepaths_list

    @staticmethod
    def load_df_from_csv(filepath):
        return pd.read_csv(filepath, comment="#")

    @classmethod
    def build_df_for_data_source_type(cls, data_source):
        # There may be multiple files for a particular data source type
        data_source_df = pd.concat(
            [cls.load_df_from_csv(filepath) for filepath in data_source[DATA_LOCATION]]
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
                data_source_df, how="inner", left_on=left_keys, right_on=right_keys,
            )
        return combined_data_table

    def get_schema_for_data_source(self):
        """
        :return: list of named tuples that contain the name and data type of the df columns
        This is designed to match the data format of the column tuples used in sqlalchemy
        """
        return self.combined_data_table.columns

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

    def get_table_data(self, filters: list = None) -> dict:
        df = self.combined_data_table
        if filters is None:
            filters = []
        for filter_dict in filters:
            column = df[filter_dict[OPTION_COL]]
            df = df[local_csv_handler_filter_operation(column, filter_dict)]
        return df

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
    """
    Used for getting meta data information and uploading to backend
    """

    def __init__(self, data_sources):
        # Instance methods for this class refer to single data source table
        assert len(data_sources) == 1
        self.data_source_name = data_sources[MAIN_DATA_SOURCE][DATA_SOURCE_TYPE]
        self.data_file_directory = os.path.join(
            current_app.config[CONFIG_FILE_FOLDER], DATA, self.data_source_name
        )

    @staticmethod
    def get_available_data_sources():
        data_folders = [
            f.name
            for f in os.scandir(
                os.path.join(current_app.config[CONFIG_FILE_FOLDER], DATA)
            )
            if f.is_dir()
        ]
        existing_data_sources = [x for x in data_folders if x != DATA_UPLOAD_METADATA]
        return existing_data_sources

    @classmethod
    def get_data_upload_metadata(cls, data_source_names):
        """
        Get a dicts of lists of all of the files by data source type,
        along with any metadata we have about the files
        :param data_source_names: list of data sources
        :param active_filter:
        :return: dict keyed by table name, valued with list of dicts describing the upload
        """
        data_upload_metadata = cls.get_data_upload_metadata_df()
        files_by_data_source = {}
        for data_source_name in data_source_names:
            full_path = os.path.join(
                current_app.config[CONFIG_FILE_FOLDER], DATA, data_source_name,
            )
            list_of_files = glob.glob(f"{full_path}/*.csv")
            assert len(list_of_files) > 0
            files_by_data_source[data_source_name] = [
                os.path.basename(f) for f in list_of_files
            ]
        identifiers_by_table = defaultdict(list)
        # for each file identifier in the file system, match up any metadata we have
        for data_source_name, data_source_identifiers in files_by_data_source.items():
            for data_source_identifier in data_source_identifiers:
                corresponding_metadata_row = data_upload_metadata[
                    data_upload_metadata.upload_id == data_source_identifier
                ]
                if corresponding_metadata_row.empty:
                    metadata_row_dict = {}
                else:
                    metadata_row_dict = corresponding_metadata_row.to_dict("records")[0]
                identifier_row = {
                    UPLOAD_ID: data_source_identifier,
                    USERNAME: metadata_row_dict.get(USERNAME),
                    UPLOAD_TIME: metadata_row_dict.get(UPLOAD_TIME),
                    ACTIVE: metadata_row_dict.get(ACTIVE),
                    NOTES: metadata_row_dict.get(NOTES),
                }
                identifiers_by_table[data_source_name].append(identifier_row)
        return identifiers_by_table

    @classmethod
    def _get_updated_metadata_df_for_csv_write(cls, data_source_name, active_data_dict):
        """
        Called by update_data_upload_metadata_active- function formatted with a return
        for testing, since update_data_upload_metadata_active writes a file as output
        :param data_source_name: data source folder name
        :param active_data_dict: dict keyed by upload_id/file paths, valued with string INACTIVE or ACTIVE
        :return: pandas dataframe containing entire updated data_upload_metadata_df
        """
        data_upload_metadata = cls.get_data_upload_metadata_df()
        for upload_id, active_str in active_data_dict.items():
            active_status = active_str == ACTIVE
            row_inds = (data_upload_metadata.table_name == data_source_name) & (
                data_upload_metadata.upload_id == upload_id
            )
            if data_upload_metadata[row_inds].empty:
                # there was no existing row for this file in the metadata records-
                # create a new one
                new_row = pd.DataFrame(
                    [
                        {
                            UPLOAD_ID: upload_id,
                            ACTIVE: active_status,
                            UPLOAD_TIME: None,
                            TABLE_NAME: data_source_name,
                            NOTES: None,
                            USERNAME: None,
                        }
                    ]
                )
                data_upload_metadata = pd.concat([data_upload_metadata, new_row])
            else:
                # update an existing row corresponding to this file
                data_upload_metadata.loc[row_inds, ACTIVE] = active_status
        return data_upload_metadata.reset_index(drop=True)

    @classmethod
    def update_data_upload_metadata_active(cls, data_source_name, active_data_dict):
        """
        Edits the data_upload_metadata file to indicate the active/inactive status of
        files as selected in the admin panel of the app
        :param data_source_name: data source folder name
        :param active_data_dict: dict keyed by upload_id/file paths, valued with string INACTIVE or ACTIVE
        :return: None. Writes a modified dataframe to the data_upload_metadata.csv
        """
        data_upload_metadata = cls._get_updated_metadata_df_for_csv_write(
            data_source_name, active_data_dict
        )
        data_upload_metadata.to_csv(cls.get_data_upload_metadata_path(), index=False)

    def delete_data_source(self):
        # if there are files in this data source directory, clear it out
        if os.path.exists(self.data_file_directory):
            shutil.rmtree(self.data_file_directory)
        # remove rows corresponding to this datasource from the metadata file
        data_upload_metadata = self.get_data_upload_metadata_df()
        data_upload_metadata = data_upload_metadata[
            data_upload_metadata[TABLE_NAME] != self.data_source_name
        ]
        data_upload_metadata.to_csv(self.get_data_upload_metadata_path(), index=False)

    def write_data_upload_to_backend(
        self, uploaded_data_df, username, notes, filename=None
    ):
        """
        :param file_name: str
        :param uploaded_data_df: pandas dataframe on which we have already done validation
        :param username: str
        :param notes: str
        :return: Empty list representing columns not in the new file that are in the old. Included for function signature matching
        """
        upload_time = datetime.utcnow()
        filename = (
            upload_time.strftime(DATETIME_FORMAT)
            if (filename is None)
            else sanitize_filename(secure_filename(filename))
        )
        filename = (
            filename if filename.endswith(".csv") else "".join([filename, ".csv"])
        )

        if not os.path.exists(self.data_file_directory):
            os.makedirs(self.data_file_directory)
        file_path = os.path.join(self.data_file_directory, filename)
        if os.path.exists(file_path):
            raise ValidationError(
                f"Filename {filename} already exists for data source type {self.data_source_name}"
            )
        # write UPLOAD_ID and INDEX_COLUMN to match SQL handler
        uploaded_data_df[UPLOAD_ID] = filename
        uploaded_data_df.to_csv(file_path, index_label=INDEX_COLUMN)

        # update the data upload metadata
        data_upload_metadata = self.get_data_upload_metadata_df()
        new_row = {
            UPLOAD_ID: filename,
            TABLE_NAME: self.data_source_name,
            USERNAME: username,
            NOTES: notes,
            ACTIVE: True,
            UPLOAD_TIME: upload_time,
        }
        data_upload_metadata = pd.concat(
            [data_upload_metadata, pd.DataFrame([new_row])]
        )
        data_upload_metadata.to_csv(self.get_data_upload_metadata_path(), index=False)

        return []
