# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

"""
Create a table in your SQL db defined by a csv file. This is paired with sqlalchemy
codegen to create entries in the model file for the table.

Schema extraction inspired by:
https://hackersandslackers.com/infer-datatypes-from-csvs-to-create/
"""

from collections import OrderedDict
from datetime import datetime
import sys
from io import StringIO
import re

import pandas as pd

import psycopg2  # used here for fast copy_from performance
from sqlalchemy import create_engine, Table, MetaData, Column
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func
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

from app_deploy_data.app_settings import DATABASE_CONFIG
from utility.constants import INDEX_COLUMN, UPLOAD_ID, UPLOAD_TIME

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
EXISTS_OPTIONS = [REPLACE, APPEND, FAIL]
POSTGRES_TABLE_NAME_FORMAT_REGEX = r"^[a-zA-Z_]\w+$"


def connect(db_config_dict):
    """ Connect to the PostgreSQL database server """
    config_dict = {
        k: v
        for k, v in db_config_dict.items()
        if k in ["host", "password", "database", "user"]
    }
    print(config_dict)
    try:
        # connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**config_dict)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    print("Connection successful")
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
        print("Copying csv done")
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        conn.rollback()
        return False
    finally:
        cursor.close()


class CreateTablesFromCSVs:
    """Infer a table schema from a CSV."""

    def __init__(self, db_config):
        self.db_config = db_config
        connection_url = URL(**self.db_config)
        self.engine = create_engine(connection_url)
        self.Base = None
        self.reflect_db_tables_to_sqlalchemy_classes()
        self.db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )

    def get_upload_id_for_table(self, table_name):
        # get the max upload id currently associated with the table and increment it
        upload_metadata = self.Base.classes.data_upload_metadata
        result = (
            self.db_session.query(func.max(upload_metadata.upload_id))
            .filter(upload_metadata.table_name == table_name)
            .first()
        )
        max_upload_id = result[0]  # always defined- tuple with None if no result
        # if there were no entries in the table for this upload ID, set default
        max_upload_id = max_upload_id or 0
        upload_id = max_upload_id + 1
        return upload_id

    def create_and_fill_new_sql_table_from_df(self, table_name, data, if_exists):

        key_column = None
        print(f"Creating empty table named {table_name}")
        upload_id = self.get_upload_id_for_table(table_name)
        upload_time = datetime.utcnow()
        data = self.append_metadata_to_data(
            data, upload_id=upload_id, upload_time=upload_time, key_columns=key_column,
        )
        data, schema = self.get_schema_from_df(data)
        # this creates an empty table of the correct schema using pandas to_sql
        self.create_new_table(
            table_name, schema, key_columns=key_column, if_exists=if_exists
        )
        # bulk copy of the contents using psycopg2 copy_from, which is much faster, see:
        # https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/
        psycopg2_config_dict = {
            "host": self.db_config["host"],
            "database": self.db_config["database"],
            "user": self.db_config["username"],
            "password": self.db_config["password"],
        }
        conn = connect(psycopg2_config_dict)
        success = psycopg2_copy_from_stringio(conn, data, table_name)
        if not success:
            raise Exception
        return upload_id, upload_time, table_name

    def reflect_db_tables_to_sqlalchemy_classes(self):
        self.Base = automap_base()
        # reflect the tables present in the sql database as sqlalchemy models
        self.Base.prepare(self.engine, reflect=True)

    def write_upload_metadata_row(self, upload_id, upload_time, table_name, active):
        upload_metadata = self.Base.classes.data_upload_metadata
        row = upload_metadata(
            upload_id=upload_id,
            upload_time=upload_time,
            table_name=table_name,
            active=active,
        )
        self.db_session.add(row)
        self.db_session.commit()

    @staticmethod
    def get_data_from_csv(csv_data_file_path):
        """
        :param csv_data_file_path:
        :return: pandas dataframe
        """
        return pd.read_csv(csv_data_file_path, encoding="utf-8", comment="#")

    @classmethod
    def get_schema_from_df(cls, data):
        """
        Infers schema from df file

        :return: schema_dict of names:data_types
        """

        def convert_to_nullable_int_if_able(x):
            # Pandas stores numerics with nulls as floats. Int64 (not int64) is nullable
            # Use this dtype where appropriate
            try:
                return x.astype("Int64")
            except TypeError:
                return x

        data_cast = data.apply(convert_to_nullable_int_if_able)
        df_pandas_schema_dict = {}
        for column in data_cast.columns:
            df_pandas_schema_dict[column] = pd.api.types.infer_dtype(data_cast[column])
        df_sql_schema_dict = {
            k: SQL_DATA_TYPE_MAP[v] for k, v in df_pandas_schema_dict.items()
        }
        metadata_schema = OrderedDict(
            {UPLOAD_ID: Integer, UPLOAD_TIME: DateTime, INDEX_COLUMN: Integer,}
        )
        metadata_schema.update(df_sql_schema_dict)
        return data_cast, metadata_schema

    @staticmethod
    def append_metadata_to_data(
        data, upload_id, upload_time, key_columns=None,
    ):
        # if there is no key specified, include the index
        index = key_columns is not None
        if not index:
            # assign row numerical index to its own column
            data = data.reset_index()
            data.rename(columns={"index": INDEX_COLUMN}, inplace=True)
        # add upload_id and time column to the table at the first columns of the df
        data.insert(0, UPLOAD_TIME, upload_time)
        data.insert(0, UPLOAD_ID, upload_id)
        return data

    def create_new_table(
        self, table_name, schema, key_columns, if_exists,
    ):
        """
        Create an EMPTY table from CSV and generated schema.
        Empty table because the ORM copy function is very slow- we'll populate the table
        data using a lower-level interface to SQL
        """

        meta = MetaData(bind=self.engine)
        meta.reflect()
        table_object = meta.tables.get(table_name)
        if table_object is not None:
            if if_exists == REPLACE:
                meta.drop_all(tables=[table_object])
                print(
                    f"Table {table_name} already exists- "
                    f"dropping and replacing as per argument"
                )
                meta.clear()
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
        _ = Table(table_name, meta, *columns)
        meta.create_all()


if __name__ == "__main__":
    """
    example usage:
    python database/csv_to_sql.py penguin_size escalation/test_app_deploy_data/data/penguin_size/penguin_size.csv replace
    create a models.py file with the sqlalchemy models of the tables in the db
    sqlacodegen postgresql+pg8000://escalation_os:escalation_os_pwd@localhost:54320/escalation_os --outfile app_deploy_data/models.py

    """
    table_name = sys.argv[1]
    filepath = sys.argv[2]
    if_exists = sys.argv[3]
    # todo - better arg handling with argparse or something
    assert if_exists in EXISTS_OPTIONS

    if not re.match(POSTGRES_TABLE_NAME_FORMAT_REGEX, table_name):
        print(
            "Table names name must start with a letter or an underscore;"
            " the rest of the string can contain letters, digits, and underscores."
        )
        exit(1)
    if len(table_name) > 31:
        print(
            "Postgres SQL only supports table names with length <= 31-"
            " additional characters will be ignored"
        )
        exit(1)
    if re.match("[A-Z]", table_name):
        print(
            "Postgres SQL table names are case insensitive- "
            "tablename will be converted to lowercase letters"
        )

    db_config = DATABASE_CONFIG
    csv_sql_writer = CreateTablesFromCSVs(db_config)

    data = csv_sql_writer.get_data_from_csv(filepath)
    (
        upload_id,
        upload_time,
        table_name,
    ) = csv_sql_writer.create_and_fill_new_sql_table_from_df(
        table_name, data, if_exists
    )
    csv_sql_writer.write_upload_metadata_row(
        upload_id, upload_time, table_name, active=True
    )
