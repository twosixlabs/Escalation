# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

"""
Create a table in your SQL db defined by a csv file. This is paired with sqlalchemy
codegen to create entries in the model file for the table.

This script assumes you are running locally, and have a Docker container running the database as per readme

In order to create new tables, the app must be running in setup wizard mode
"""

import sys
import re

import requests

from utility.constants import DATA_SOURCE, CSVFILE, POSTGRES_TABLE_NAME_FORMAT_REGEX

REPLACE = "replace"
APPEND = "append"
FAIL = "fail"
EXISTS_OPTIONS = [REPLACE, APPEND]

if __name__ == "__main__":
    """
    example usage:
    python scripts/csv_to_sql.py penguin_size test_app_deploy_data/data/penguin_size/penguin_size.csv append my_user "this is from the experiment 2020-09-10"
    """
    # todo - better arg handling with argparse or something

    table_name = sys.argv[1]
    filepath = sys.argv[2]
    if_exists = sys.argv[3]
    username = sys.argv[4]
    notes = sys.argv[5]

    assert if_exists in EXISTS_OPTIONS

    if if_exists == REPLACE:
        FLASK_UPLOAD_URL = "http://localhost:8000/wizard/upload"
    else:
        FLASK_UPLOAD_URL = "http://localhost:8000/upload"

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
    try:
        response = requests.post(
            FLASK_UPLOAD_URL,
            data={DATA_SOURCE: table_name, "username": username, "notes": notes,},
            files=[(CSVFILE, open(filepath, "rb")),],
            # to upload more than one file at a time, need to provide a list like this
            # files=[
            #     (CSVFILE, open("file1.csv", "rb")),
            #     (CSVFILE, open("file_2.csv", "rb")),
            # ],
        )
    except Exception:
        raise (
            Exception,
            "Is escalation running in debug mode?",
        )

    if response.status_code != 200:
        raise (
            Exception,
            f"Unable to post data to Escalation server: {response.status_code}",
        )
