# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
from collections import OrderedDict, defaultdict
from datetime import datetime
from io import StringIO
import sys

from flask import current_app
import pandas as pd
import psycopg2
from sqlalchemy import and_, func, create_engine, MetaData, Column, Table
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.types import (
    Integer,
    Text,
    DateTime,
    Float,
    Boolean,
    Date,
    JSON,
    Time,
    ARRAY,
    Interval,
)

from database.data_handler import DataHandler
from operator import eq, gt, ge, le, lt

from utility.available_selectors import (
    get_key_for_form,
    get_base_info_for_selector,
    make_filter_dict,
    convert_string_for_numerical_filter,
)

from utility.constants import *

# from: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.api.types.infer_dtype.html
SQL_DATA_TYPE_MAP = {
    "integer": Integer,
    "floating": Float,
    "decimal": Float,
    "mixed-integer-float": Float,
    "string": Text,
    "mixed-integer": Text,
    "category": Text,
    "bytes": Text,
    "date": DateTime,
    "datetime64": DateTime,
    "datetime": DateTime,
    "datetime.date": Date,
    "time": Time,
    "timedelta64": Interval,
    "timedelta": Interval,
    "dict": JSON,
    "list": ARRAY,
    "boolean": Boolean,
}


REPLACE = "replace"
APPEND = "append"
FAIL = "fail"

OPERATIONS_FOR_NUMERICAL_FILTERS = OrderedDict(
    [(">", gt), (">=", ge), ("=", eq), ("<=", le), ("<", lt)]
)
NUMERICAL_FILTER_DICT = {MAX: "<=", MIN: ">="}


def sql_handler_filter_operation(data_column, filter_dict):
    """
    Applies filter operations for queries in the SqlHandler.
    :param data_column: sql column object
    :param filter_dict:
    :return: an operation function that can be applied on the query when executed
    """
    if filter_dict[SELECTOR_TYPE] == FILTER:
        entry_values_to_be_shown_in_plot = filter_dict[SELECTED]  # Always a list
        # data backends may handle a single value differently from multiple values for performance reasons
        if len(entry_values_to_be_shown_in_plot) > 1:
            return data_column.in_(entry_values_to_be_shown_in_plot)
        else:
            return eq(data_column, entry_values_to_be_shown_in_plot[0])
    elif filter_dict[SELECTOR_TYPE] == NUMERICAL_FILTER:
        operation_function = OPERATIONS_FOR_NUMERICAL_FILTERS[filter_dict[OPERATION]]
        return operation_function(data_column, filter_dict[VALUE])


def connect_to_db_using_psycopg2():
    # bulk copy of the contents using psycopg2 copy_from, which is much faster, see:
    # https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/

    """ Connect to the PostgreSQL database server """
    url_obj = current_app.config[SQLALCHEMY_DATABASE_URI]
    psycopg2_config_dict = {
        "host": url_obj.host,
        "database": url_obj.database,
        "user": url_obj.username,
        "password": url_obj.password,
    }
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**psycopg2_config_dict)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    return conn


def psycopg2_copy_from_stringio(conn, df, table_name):
    """
    Here we are going save the dataframe in memory
    and use copy_from() to copy it to the table
    """
    # save dataframe to an in-memory buffer to use with copy_from, which requires fil
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    cursor = conn.cursor()
    # todo: assert that the column order matches expectation
    try:
        # issues with separators here cause Error: extra data after last expected column
        cursor.copy_expert(f"copy {table_name} from stdin (format csv)", buffer)
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        conn.rollback()
        return False
    finally:
        cursor.close()


class SqlHandler(DataHandler):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.data_filters = []
        self.table_lookup_by_name = {}
        # create a flattened list from the data_sources object
        self.flat_data_sources = [
            self.data_sources[MAIN_DATA_SOURCE]
        ] + self.data_sources.get(ADDITIONAL_DATA_SOURCES, [])
        for data_source in self.flat_data_sources:
            table_name = data_source[DATA_SOURCE_TYPE]
            table_class = self.get_class_name_from_table_name(table_name)
            self.table_lookup_by_name[table_name] = table_class
            data_source.update({DATA_LOCATION: table_class})
        self.column_lookup_by_name = self.build_combined_data_table()

    @staticmethod
    def get_class_name_from_table_name(table_name):
        """
        Camel-cased class name generated by sqlalchemy codegen doesn't match the sql table name. Fetch the class name based on matching class table name
        :param tablename str
        :return: table class object
        """
        return current_app.Base.metadata.tables[table_name]

    def apply_filters_to_query(self, query, filters):
        # add filters to the query dynamically
        filter_tuples = []
        for filter_dict in filters:
            if not (
                filter_dict[SELECTOR_TYPE] == NUMERICAL_FILTER or filter_dict[SELECTED]
            ):
                # No filter has been applied
                continue
            column_name = self.sanitize_column_name(filter_dict[OPTION_COL])
            column_object = self.column_lookup_by_name[column_name]
            filter_tuples.append(
                sql_handler_filter_operation(column_object, filter_dict)
            )
        if filter_tuples:
            query = query.filter(*filter_tuples)
        return query

    def build_combined_data_table(self):
        """
        This takes the tables specified in self.data_sources and combines them into one easily referenceable selectable.
        This is essentially a query view- performing the joins and getting all columns that can be filtered in a query.

        :return: dictionary keyed by column names and valued with SqlAlchemy column objects
        """
        # first build a query that will get all of the columns for all of active data in the requested tables
        query = current_app.db_session.query(*list(self.table_lookup_by_name.values()))
        # specify how the different data sources are joined
        for data_source in self.data_sources.get(ADDITIONAL_DATA_SOURCES, []):
            join_clauses = []
            for left_join_key, right_join_key in data_source[JOIN_KEYS]:
                left_table_name, left_column_name = left_join_key.split(
                    TABLE_COLUMN_SEPARATOR
                )
                right_table_name, right_column_name = right_join_key.split(
                    TABLE_COLUMN_SEPARATOR
                )
                left_table = self.table_lookup_by_name[left_table_name]
                right_table = self.table_lookup_by_name[right_table_name]
                join_clauses.append(
                    (
                        getattr(left_table.columns, left_column_name)
                        == getattr(right_table.columns, right_column_name)
                    )
                )
            query = query.join(data_source[DATA_LOCATION], and_(*join_clauses))

        column_lookup_by_name = {c.name: c for c in query.selectable.alias().columns}
        return column_lookup_by_name

    def build_filters_from_active_data_source(self):
        current_tables = list(self.table_lookup_by_name.keys())
        upload_rows = SqlDataInventory.get_data_upload_metadata(current_tables)
        active_upload_rows = {
            table_name: [r for r in rows if r.get(ACTIVE)]
            for table_name, rows in upload_rows.items()
        }
        active_data_source_filters = []
        for (table_name, upload_rows,) in active_upload_rows.items():
            active_data_source_filters.append(
                {
                    OPTION_TYPE: FILTER,
                    OPTION_COL: f"{table_name}:{UPLOAD_ID}",
                    SELECTED: [r[UPLOAD_ID] for r in upload_rows],
                }
            )
        return active_data_source_filters

    @staticmethod
    def sanitize_column_name(column_name):
        # todo: better match how our auto schema is working to catch all rename logic
        return column_name.replace(TABLE_COLUMN_SEPARATOR, "_")

    def get_column_names_for_data_source(self):
        """
        gets the column names for the current handler object
        :return: list of sqlalchemy column objects
        """
        return [
            TABLE_COLUMN_SEPARATOR.join([data_source, c.name])
            for data_source, column_object in self.table_lookup_by_name.items()
            for c in column_object.columns
        ]

    def get_schema_for_data_source(self):
        """
        gets the data type for each column for the current handler object
        :return: dict keyed by column name, valued with sqlalchemy column objects
        """
        return {
            TABLE_COLUMN_SEPARATOR.join([data_source, c.name]): c.type
            for data_source, column_object in self.table_lookup_by_name.items()
            for c in column_object.columns
        }

    def get_column_data(self, columns: set, orient="list") -> dict:
        filters = self.data_filters
        all_to_include_cols = columns.union(
            [filter_dict[OPTION_COL] for filter_dict in filters]
        )

        all_column_rename_dict = {
            self.sanitize_column_name(c): c for c in all_to_include_cols
        }
        # build basic query requesting all of the columns needed
        query = current_app.db_session.query(
            *[self.column_lookup_by_name[c] for c in all_column_rename_dict.keys()]
        )
        if self.only_use_active:
            active_data_filters = self.build_filters_from_active_data_source()
            filters.extend(active_data_filters)
        query = self.apply_filters_to_query(query, filters)
        response_rows = query.all()
        if response_rows:
            # rename is switching the '_' separation back to TABLE_COLUMN_SEPARATOR
            response_as_df = pd.DataFrame(response_rows).rename(
                columns=all_column_rename_dict
            )
        else:
            # if the sql query returns no rows, we want an empty df to format our response
            response_as_df = pd.DataFrame(columns=columns)
        return response_as_df[columns].to_dict(orient)

    def get_table_data(self, filters: [] = None) -> dict:
        """
        :param filters: Optional list specifying how to filter the requested columns based on the row values
        :return: a dict keyed by column name and valued with lists of row datapoints for the column
        """

        def remove_tablename_prefix_from_column_name(text, list_prefix):
            for prefix in list_prefix:
                prefix = f"{prefix}_"
                if text.startswith(prefix):
                    return text[len(prefix) :]
            return text

        if filters is None:
            filters = []
        # build basic query requesting all of the columns needed
        column_rename_dict = {
            c: remove_tablename_prefix_from_column_name(
                c, self.table_lookup_by_name.keys()
            )
            for c in self.column_lookup_by_name.keys()
        }
        query = current_app.db_session.query(*self.column_lookup_by_name.values())
        if self.only_use_active:
            active_data_filters = self.build_filters_from_active_data_source()
            filters.extend(active_data_filters)
        query = self.apply_filters_to_query(query, filters)
        response_rows = query.all()
        if response_rows:
            # rename is switching the '_' separation back to TABLE_COLUMN_SEPARATOR
            response_as_df = pd.DataFrame(response_rows).rename(
                columns=column_rename_dict
            )
        else:
            # if the sql query returns no rows, we want an empty df to format our response
            response_as_df = pd.DataFrame(columns=column_rename_dict.values())
        return response_as_df

    def get_column_unique_entries(self, cols, filter_active_data=True) -> dict:
        """
        :param cols: a list of column names
        :param filters: Optional list specifying how to filter the requested columns based on the row values
        :param filter_active_data: Whether to filter the column entries to only include those for active data sources
        :return: A dict keyed by column names and valued with the unique values in that column
        """
        filters = self.data_filters
        unique_dict = {}
        for col in cols:
            renamed_col = self.sanitize_column_name(col)
            sql_col_class = self.column_lookup_by_name[renamed_col]
            query = current_app.db_session.query(sql_col_class).distinct()
            if filter_active_data:
                active_data_filters = self.build_filters_from_active_data_source()
                query = self.apply_filters_to_query(query, active_data_filters)
            # if the current column matches one in the filter list marked as filtered,
            # apply the filters before looking for unique values
            if any(
                [
                    (
                        filter_[COLUMN_NAME] == col
                        and filter_.get(FILTERED_SELECTOR, False)
                    )
                    for filter_ in filters
                ]
            ):
                query = self.apply_filters_to_query(query, filters)
            # we never show more than MAX_ENTRIES_NUMERICAL_COLUMN- adding one here
            # tells downstream users that there are too many values to render
            limit_values_returned = MAX_ENTRIES_FOR_FILTER_SELECTOR + 1
            response = query.limit(limit_values_returned).all()
            unique_dict[col] = [str(r[0]) for r in response if r[0] is not None]
        return unique_dict

    def get_column_unique_entries_based_on_type(self, cols, filter_active_data=True):
        """
        We only allow numerical data types to be filtered with a numerical inequality filter,
        and any data column with fewer than MAX_ENTRIES_FOR_FILTER_SELECTOR unique entries
        to be filtered by identity matching
        """
        column_types_dict = self.get_schema_for_data_source()
        unique_entries_dict = self.get_column_unique_entries(cols, filter_active_data)
        numerical_types = [Integer, Float, DateTime]
        unique_entries_dict_copy = {}
        numerical_filter_column_names = []
        filter_column_names = []
        for col_name, list_of_entries in unique_entries_dict.items():
            if any(
                [
                    isinstance(column_types_dict[col_name], num_type)
                    for num_type in numerical_types
                ]
            ):
                numerical_filter_column_names.append(col_name)
            if len(list_of_entries) <= MAX_ENTRIES_FOR_FILTER_SELECTOR:
                filter_column_names.append(col_name)
                unique_entries_dict_copy[col_name] = list_of_entries
        filter_dict = {
            FILTER: filter_column_names,
            NUMERICAL_FILTER: numerical_filter_column_names,
        }
        return unique_entries_dict_copy, filter_dict

    def add_instructions_to_config_dict(self):
        if self.selectable_data_dict:
            self.add_active_selectors_to_selectable_data_list()
            if self.addendum_dict:
                self.add_operations_to_the_data_from_addendum()
            else:
                self.add_operations_to_the_data_from_defaults()

    def add_active_selectors_to_selectable_data_list(self):
        """
        Sets which selectors are active based on user choices.
        If none have been selected sets reasonable defaults
        :return:
        """
        filter_list = self.selectable_data_dict.get(FILTER, [])
        for index, filter_dict in enumerate(filter_list):

            selected_filters = self.addendum_dict.get(
                get_key_for_form(FILTER, index), []
            )
            if SHOW_ALL_ROW in selected_filters:
                filter_dict[ACTIVE_SELECTORS] = [SHOW_ALL_ROW]
            else:
                filter_dict[ACTIVE_SELECTORS] = (
                    selected_filters
                    or filter_dict.get(DEFAULT_SELECTED)
                    or [SHOW_ALL_ROW]
                )

        numerical_filter_list = self.selectable_data_dict.get(NUMERICAL_FILTER, [])
        for index, numerical_filter_dict in enumerate(numerical_filter_list):
            extrema = [MAX, MIN]
            active_numerical_filter_dict = defaultdict(dict)
            for extremum in extrema:
                # pull the relevant filter info from the submitted form
                # all values in addendum_dict are lists
                numerical_filter_value = self.addendum_dict.get(
                    NUMERICAL_FILTER_NUM_LOC_TYPE.format(index, extremum, VALUE)
                )
                active_numerical_filter_dict[extremum][VALUE] = (
                    numerical_filter_value[0]
                    if numerical_filter_value
                    else numerical_filter_dict.get(extremum, "")
                )

            numerical_filter_dict[ACTIVE_SELECTORS] = active_numerical_filter_dict

    def add_operations_to_the_data_from_addendum(self):
        """
        Adds operations to be passed to the data handlers for the data
        Broken into two major parts read in info from selection_dict and addendum_dict and then
         output a filter dict or change visualization_info_list or data_info_dict depending on the kind of filter
        :selectable_data_dict: each element of the dictionary on is how to build the selector on the webpage
        :addendum_dict: User selections form the webpage
        :return:
        """
        operation_list = []

        # creates an operations where only the values selected along a column will be shown in the plot
        filter_list = self.selectable_data_dict.get(FILTER, [])
        for index, filter_dict in enumerate(filter_list):
            base_info_dict_for_selector = get_base_info_for_selector(
                filter_dict, FILTER
            )
            selection = self.addendum_dict.get(get_key_for_form(FILTER, index))
            if len(selection) == 0 or SHOW_ALL_ROW in selection:
                continue
            base_info_dict_for_selector[SELECTED] = selection
            base_info_dict_for_selector[FILTERED_SELECTOR] = filter_dict.get(
                FILTERED_SELECTOR, False
            )
            operation_list.append(base_info_dict_for_selector)

        # creates an operations where only the values following an (in)equality
        # along a column will be shown in the plot
        numerical_filter_list = self.selectable_data_dict.get(NUMERICAL_FILTER, [])
        for index, numerical_filter_dict in enumerate(numerical_filter_list):
            base_info_dict_for_selector = get_base_info_for_selector(
                numerical_filter_dict, NUMERICAL_FILTER
            )
            # the numerical filter contains two filters so add them separately
            for extremum in [MAX, MIN]:
                # get the value submitted in the web form by using its name
                # format specified in numeric_filter.html
                # the value is a list of length one
                numerical_value = self.addendum_dict[
                    NUMERICAL_FILTER_NUM_LOC_TYPE.format(index, extremum, VALUE)
                ][0]
                if numerical_value == "":
                    continue

                numerical_filter_info = {
                    VALUE: convert_string_for_numerical_filter(numerical_value),
                    OPERATION: NUMERICAL_FILTER_DICT[extremum],
                }
                operation_list.append(
                    {**base_info_dict_for_selector, **numerical_filter_info}
                )
        self.data_filters = operation_list

    def add_operations_to_the_data_from_defaults(self):
        """
        Adds operations to be passed to the data handlers for the data
        Broken into two major parts read in info from selection_dict and then output a filter dict
        :selectable_data_dict: each filter element of the dict is a list of dictionary on how to build
        the selector on the webpage
        :return:
        """
        operation_list = []
        filter_list = self.selectable_data_dict.get(FILTER, [])
        for index, filter_dict in enumerate(filter_list):
            if DEFAULT_SELECTED in filter_dict:
                base_info_dict_for_selector = get_base_info_for_selector(
                    filter_dict, FILTER
                )
                selection = filter_dict.get(DEFAULT_SELECTED)
                # make sure we don't have an empty selection list,
                #  or a list that only contains an empty string
                if selection and selection != [""]:
                    base_info_dict_for_selector[SELECTED] = (
                        selection if isinstance(selection, list) else [selection]
                    )
                    base_info_dict_for_selector[FILTERED_SELECTOR] = filter_dict.get(
                        FILTERED_SELECTOR, False
                    )
                    operation_list.append(base_info_dict_for_selector)

        numerical_filter_list = self.selectable_data_dict.get(NUMERICAL_FILTER, [])
        for index, numerical_filter_dict in enumerate(numerical_filter_list):
            for extremum in [MAX, MIN]:
                numerical_value = numerical_filter_dict.get(extremum)
                if numerical_value == "" or numerical_value is None:
                    continue
                base_info_dict_for_selector = get_base_info_for_selector(
                    numerical_filter_dict, NUMERICAL_FILTER
                )
                numerical_filter_info = {
                    VALUE: convert_string_for_numerical_filter(numerical_value),
                    OPERATION: NUMERICAL_FILTER_DICT[extremum],
                }
                operation_list.append(
                    {**base_info_dict_for_selector, **numerical_filter_info}
                )
        if operation_list:
            self.data_filters = operation_list

    def get_columns_that_need_unique_entries(self) -> set:
        """
        extracts what data are needed for the selectors
        :param plot_options:
        :return:
        """
        filter_list = self.selectable_data_dict.get(FILTER, [])
        column_list = {
            filter_dict[OPTION_COL]
            for filter_dict in filter_list
            if filter_dict.get(VISIBLE, True)
        }
        return column_list

    def create_data_subselect_info_for_plot(self):
        """
        puts selector data in form to be read by html file
        Broken into two major parts read in info from selection_option_dict_for_plot and then populate
         select_info elements
        :param plot_specification:
        :param data_handler:
        :return:
        """
        if not self.unique_entry_dict:
            self.unique_entry_dict = self.get_column_unique_entries(
                self.get_columns_that_need_unique_entries()
            )
        filter_list = self.selectable_data_dict.get(FILTER, [])
        for index, filter_dict in enumerate(filter_list):
            if filter_dict.get(VISIBLE, True):
                column = filter_dict[OPTION_COL]

                selector_entries = self.unique_entry_dict[column]
                selector_entries.sort()
                # append show_all_rows to the front of the list
                selector_entries.insert(0, SHOW_ALL_ROW)
                self.select_info.append(
                    make_filter_dict(FILTER, filter_dict, index, selector_entries)
                )

        numerical_filter_list = self.selectable_data_dict.get(NUMERICAL_FILTER, [])
        for index, numerical_filter_dict in enumerate(numerical_filter_list):
            if numerical_filter_dict.get(VISIBLE, True):
                self.select_info.append(
                    make_filter_dict(NUMERICAL_FILTER, numerical_filter_dict, index)
                )


class DataFrameConverter:
    """
    Shared helper methods that convert schemas between pandas and sql, alter data types,
    and add metadata to dataframes to match the expectations of the database.
    """

    @staticmethod
    def cast_dataframe_datatypes(data):
        def convert_to_nullable_int_if_able(x):
            # Pandas stores numerics with nulls as floats. Int64 (not int64) is nullable
            # Use this dtype where appropriate
            try:
                return x.astype("Int64")
            except TypeError:
                return x

        return data.apply(convert_to_nullable_int_if_able)

    @classmethod
    def get_schema_from_df(cls, data):
        """
        Infers schema from pandas df
        :return: schema_dict of names:data_types
        """

        data_cast = cls.cast_dataframe_datatypes(data)
        df_pandas_schema_dict = {}
        for column in data_cast.columns:
            df_pandas_schema_dict[column] = pd.api.types.infer_dtype(data_cast[column])
        df_sql_schema_dict = {
            k: SQL_DATA_TYPE_MAP[v] for k, v in df_pandas_schema_dict.items()
        }
        metadata_schema = OrderedDict({UPLOAD_ID: Integer, INDEX_COLUMN: Integer,})
        metadata_schema.update(df_sql_schema_dict)
        return data_cast, metadata_schema

    @staticmethod
    def append_metadata_to_data(data, upload_id, key_columns=None):
        """
        :param data: pandas df
        :param upload_id: integer upload id
        :param key_columns: user-specified primary key columns, if any
        :return: modified df with metadata columns
        """
        # if there is no key specified, include the index
        index = key_columns is not None
        if not index:
            # assign row numerical index to its own column
            data = data.reset_index()
            data.rename(columns={"index": INDEX_COLUMN}, inplace=True)
        # add upload_id and time column to the table at the first columns of the df
        data.insert(0, UPLOAD_ID, upload_id)
        return data


class SqlDataInventory(SqlHandler, DataFrameConverter):
    """
    Used for getting meta data information and uploading to backend
    """

    def __init__(self, data_sources):
        # Instance methods for this class refer to single data source table
        assert len(data_sources) == 1
        super().__init__(data_sources)
        self.data_source_name = [*self.table_lookup_by_name.keys()][0]

    @staticmethod
    def get_sqlalchemy_model_class_for_data_upload_metadata():
        """
        Return the DataUploadMetadata class associated with the current base.
        This is more complicated than simply importing from a file,
         because we use different paths for testing environments
        :return: sqlalchemy model class for DATA_UPLOAD_METADATA
        """
        for c in current_app.Base._decl_class_registry.values():
            if hasattr(c, "__tablename__") and c.__tablename__ == DATA_UPLOAD_METADATA:
                return c
        raise KeyError(f"{DATA_UPLOAD_METADATA} not found in available model classes")

    @staticmethod
    def get_available_data_sources():
        """
        Lists all data sources available in the db
        :return:
        """
        return [
            table_name
            for table_name in current_app.Base.metadata.tables.keys()
            if table_name != DATA_UPLOAD_METADATA
        ]

    @classmethod
    def write_upload_metadata_row(
        cls, table_name, upload_time, upload_id, username, notes, active=True
    ):
        data_upload_metadata = cls.get_sqlalchemy_model_class_for_data_upload_metadata()
        row = data_upload_metadata(
            upload_id=upload_id,
            upload_time=upload_time,
            table_name=table_name,
            active=active,
            username=username,
            notes=notes,
        )
        current_app.db_session.add(row)
        current_app.db_session.commit()

    @classmethod
    def update_data_upload_metadata_active(cls, data_source_name, active_data_dict):
        """
        Edits the data_upload_metadata table to indicate the active/inactive status of uploads as indicated in the admin panel
        :param data_source_name: data source table name
        :param active_data_dict: dict keyed by upload_id, valued with string INACTIVE or ACTIVE
        :return: None. updates rows in the data_upload_metadata table
        """
        data_upload_metadata = cls.get_sqlalchemy_model_class_for_data_upload_metadata()
        for upload_id, active_status in active_data_dict.items():
            # upload_id are of form f"id_{upload_id}"
            row = (
                current_app.db_session.query(data_upload_metadata)
                .filter_by(table_name=data_source_name, upload_id=upload_id[3:])
                .first()
            )
            active_boolean = active_status == ACTIVE
            row.active = active_boolean
            current_app.db_session.commit()

    @classmethod
    def get_data_upload_metadata(cls, data_source_names):
        """

        :param data_source_names: list of data sources
        :param active_filter:
        :return: dict keyed by table name, valued with list of dicts describing the upload
        """

        data_upload_metadata = cls.get_sqlalchemy_model_class_for_data_upload_metadata()
        query = current_app.db_session.query(data_upload_metadata).filter(
            data_upload_metadata.table_name.in_(data_source_names)
        )
        results = query.all()
        identifiers_by_table = defaultdict(list)
        for result in results:
            identifiers_by_table[result.table_name].append(
                {
                    UPLOAD_ID: result.upload_id,
                    USERNAME: result.username,
                    UPLOAD_TIME: result.upload_time.strftime(DATETIME_FORMAT),
                    ACTIVE: result.active,
                    NOTES: result.notes,
                }
            )
        return identifiers_by_table

    @classmethod
    def get_new_upload_id_for_table(cls, table_name):
        data_upload_metadata = cls.get_sqlalchemy_model_class_for_data_upload_metadata()
        # get the max upload id currently associated with the table and increment it
        result = (
            current_app.db_session.query(func.max(data_upload_metadata.upload_id))
            .filter(data_upload_metadata.table_name == table_name)
            .first()
        )
        max_upload_id = result[0]  # always defined- tuple with None if no result
        # if there were no entries in the table for this upload ID, set default
        max_upload_id = max_upload_id or 0
        upload_id = max_upload_id + 1
        return upload_id

    @staticmethod
    def get_upload_time():
        """Factored out for testing and for future timezone control implementation"""
        return datetime.utcnow()

    def write_data_upload_to_backend(self, uploaded_data_df, username, notes):
        """
        :param uploaded_data_df: pandas dataframe on which we have already done validation
        :param data_source_name: str
        Assumption: data_source for this upload is only one table, even though they can generally refer to more than one table
        :return: list of df columns not written to the db (no corresponding db column)
        """
        uploaded_data_df = self.cast_dataframe_datatypes(uploaded_data_df)
        table = self.table_lookup_by_name[self.data_source_name]
        new_upload_id = self.get_new_upload_id_for_table(self.data_source_name)
        uploaded_data_df = self.append_metadata_to_data(
            data=uploaded_data_df, upload_id=new_upload_id
        )
        # todo: handle custom pk columns
        # subset the columns to write to equal those in the db
        existing_columns = [c.name for c in table.columns]
        ignored_columns = set(uploaded_data_df.columns) - set(existing_columns)
        uploaded_data_df = uploaded_data_df[existing_columns]
        conn = connect_to_db_using_psycopg2()
        psycopg2_copy_from_stringio(conn, uploaded_data_df, self.data_source_name)
        self.write_upload_metadata_row(
            upload_time=self.get_upload_time(),
            upload_id=new_upload_id,
            table_name=self.data_source_name,
            active=True,
            username=username,
            notes=notes,
        )
        return ignored_columns

    @classmethod
    def remove_metadata_rows_for_table_name(cls, table_name):
        data_upload_metadata = cls.get_sqlalchemy_model_class_for_data_upload_metadata()
        metadata_rows = current_app.db_session.query(data_upload_metadata).filter(
            data_upload_metadata.table_name == table_name
        )
        metadata_rows.delete()
        current_app.db_session.commit()


class CreateTablesFromCSVs(DataFrameConverter):
    """Infer a table schema from a CSV, and create a sql table from this definition"""

    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.reflect_db_tables_to_sqlalchemy_classes()
        self.Base = None
        self.meta = MetaData(bind=self.engine)

    def create_and_fill_new_sql_table_from_df(self, table_name, data, if_exists):

        key_column = None
        print(f"Creating empty table named {table_name}")
        upload_id = SqlDataInventory.get_new_upload_id_for_table(table_name)
        upload_time = datetime.utcnow()
        data = self.append_metadata_to_data(
            data, upload_id=upload_id, key_columns=key_column,
        )
        data, schema = self.get_schema_from_df(data)
        # this creates an empty table of the correct schema using pandas to_sql
        self.create_new_table(
            table_name, schema, key_columns=key_column, if_exists=if_exists
        )
        conn = connect_to_db_using_psycopg2()
        success = psycopg2_copy_from_stringio(conn, data, table_name)
        if not success:
            raise Exception
        return upload_id, upload_time, table_name

    def reflect_db_tables_to_sqlalchemy_classes(self):
        self.Base = automap_base()
        # reflect the tables present in the sql database as sqlalchemy models
        self.Base.prepare(self.engine, reflect=True)

    @staticmethod
    def get_data_from_csv(csv_data_file_path):
        """
        :param csv_data_file_path:
        :return: pandas dataframe
        """
        df = pd.read_csv(csv_data_file_path, encoding="utf-8", comment="#")
        # convert datetime columns from the strings loaded in csv to datetime
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_datetime(df[col])
                except ValueError:
                    pass
        return df

    def create_new_table(
        self, table_name, schema, key_columns, if_exists,
    ):
        """
        Create an EMPTY table from CSV and generated schema.
        Empty table because the ORM copy function is very slow- we'll populate the table
        data using a lower-level interface to SQL
        """

        self.meta.reflect()
        table_object = self.meta.tables.get(table_name)
        if table_object is not None:
            if if_exists == REPLACE:
                self.meta.drop_all(tables=[table_object])
                print(
                    f"Table {table_name} already exists- "
                    f"dropping and replacing as per argument"
                )
                self.meta.clear()
            elif if_exists == FAIL:
                raise KeyError(
                    f"Table {table_name} already exists- failing as per argument"
                )
            elif if_exists == APPEND:
                f"Table {table_name} already exists- appending data as per argument"
                return
        # table doesn't exist- create it
        columns = []
        primary_keys = key_columns or [UPLOAD_ID, INDEX_COLUMN]
        for name, sqlalchemy_dtype in schema.items():
            if name in primary_keys:
                columns.append(Column(name, sqlalchemy_dtype, primary_key=True))

            else:
                columns.append(Column(name, sqlalchemy_dtype))
        _ = Table(table_name, self.meta, *columns)
        self.meta.create_all()
