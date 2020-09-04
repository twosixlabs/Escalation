# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

"""
Create a table in your SQL db defined by a csv file. This is paired with sqlalchemy
codegen to create entries in the model file for the table.

"""

from io import open as io_open
import os
import sys
import re

from sqlacodegen.codegen import CodeGenerator

from database.sql_handler import SqlDataInventory, CreateTablesFromCSVs
from utility.constants import SQLALCHEMY_DATABASE_URI


REPLACE = "replace"
APPEND = "append"
FAIL = "fail"
EXISTS_OPTIONS = [REPLACE, APPEND, FAIL]

if __name__ == "__main__":
    """
    example usage:
    python database/csv_to_sql.py penguin_size escalation/test_app_deploy_data/data/penguin_size/penguin_size.csv replace
    create a models.py file with the sqlalchemy models of the tables in the db
    sqlacodegen postgresql+psycopg2://escalation_os:escalation_os_pwd@localhost:54320/escalation_os --outfile app_deploy_data/models.py

    """
    table_name = sys.argv[1]
    filepath = sys.argv[2]
    if_exists = sys.argv[3]
    # todo - better arg handling with argparse or something
    assert if_exists in EXISTS_OPTIONS

    POSTGRES_TABLE_NAME_FORMAT_REGEX = r"^[a-zA-Z_]\w+$"
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

    db_config = os.environ.get(SQLALCHEMY_DATABASE_URI)
    assert db_config is not None
    csv_sql_writer = CreateTablesFromCSVs(db_config)

    data = csv_sql_writer.get_data_from_csv(filepath)
    (
        upload_id,
        upload_time,
        table_name,
    ) = csv_sql_writer.create_and_fill_new_sql_table_from_df(
        table_name, data, if_exists
    )
    SqlDataInventory.write_upload_metadata_row(
        upload_id=upload_id,
        upload_time=upload_time,
        table_name=table_name,
        active=True,
        username=None,
        notes=None,
    )

    # Write the generated model code to the specified file or standard output
    outfile = io_open(
        os.path.join("app_deploy_data", "models.py"), "w", encoding="utf-8"
    )
    # update the metadata to include all tables in the db
    csv_sql_writer.meta.reflect()
    generator = CodeGenerator(csv_sql_writer.meta, noinflect=True)
    generator.render(outfile)
