# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
from base64 import b64encode
from io import StringIO
import os

import pandas as pd
import pytest
from werkzeug.datastructures import FileStorage

from test_app_deploy_data.models import PenguinSize
from views.file_upload import validate_data_form, validate_submission_content
from utility.constants import (
    USERNAME,
    DATA_SOURCE,
    NOTES,
    CSVFILE,
    MAIN_DATA_SOURCE,
    DATA_SOURCE_TYPE,
)
from utility.exceptions import ValidationError

DATA_SOURCE_NAME = "penguin_size"
TEST_FILENAME = filename = os.path.join(
    "test_app_deploy_data", "data", "penguin_size", "penguin_size.csv"
)


@pytest.fixture
def request_form():
    return {
        USERNAME: "test_user",
        DATA_SOURCE: DATA_SOURCE_NAME,
        NOTES: "test_notes",
    }


def test_validate_submission_content(penguin_size_csv_file, test_app_client_sql_backed):
    data_handler_class = test_app_client_sql_backed.config.data_handler(
        data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: DATA_SOURCE_NAME}}
    )

    data_source_schema = data_handler_class.get_schema_for_data_source()
    try:
        _ = validate_submission_content(penguin_size_csv_file, data_source_schema)
    except ValidationError:
        pytest.fail("validate_submission_content should run without error on good file")

    df = pd.read_csv(TEST_FILENAME)
    df["extra column not in schema"] = -99
    extra_column_file = FileStorage(StringIO(df.to_csv(index=False)), filename=CSVFILE)
    try:
        validate_submission_content(extra_column_file, data_source_schema)
    except ValidationError:
        pytest.fail(
            "Extra columns in the uploaded file not in schema should be ignored"
        )

    df = pd.read_csv(TEST_FILENAME)
    df.drop("island", axis=1, inplace=True)
    missing_column_file = FileStorage(
        StringIO(df.to_csv(index=False)), filename=CSVFILE
    )
    with pytest.raises(ValidationError):
        validate_submission_content(missing_column_file, data_source_schema)


def test_validate_data_form(
    test_app_client_sql_backed, penguin_size_csv_file, request_form
):
    for required_field in [USERNAME, DATA_SOURCE, NOTES]:
        missing_field_form = request_form.copy()
        _ = missing_field_form.pop(required_field)
        with pytest.raises(ValidationError):
            validate_data_form(missing_field_form, penguin_size_csv_file)
    # todo: validate file is a real file
    # for broken_files in [{}, {CSVFILE: None}]:
    #     # require csvfile
    #     with pytest.raises(ValidationError):
    #         validate_data_form(request_form, broken_files)


def test_submission_auth_prd_mode_failures(
    test_app_client_sql_backed, request_form, penguin_size_csv_file
):
    # test authentication
    client = test_app_client_sql_backed.test_client()
    get_response = client.get("/upload")
    assert get_response.status_code == 200

    request_form[CSVFILE] = penguin_size_csv_file
    post_response = client.post("/upload", data=request_form,)
    # test responses in environment other than DEVELOPMENT- auth required
    assert post_response.status_code == 401

    # todo: test client setup should include test-specific users
    # with credentials, but no form data, we authenticate but get bad request response
    credentials = b64encode(b"admin:escalation").decode("utf-8")
    post_response = client.post(
        "/upload", headers={"Authorization": f"Basic {credentials}",},
    )
    assert post_response.status_code == 400


def test_submission_auth_prd_mode(
    test_app_client_sql_backed, request_form, penguin_size_csv_file
):
    client = test_app_client_sql_backed.test_client()
    credentials = b64encode(b"admin:escalation").decode("utf-8")
    request_form[CSVFILE] = penguin_size_csv_file
    post_response = client.post(
        "/upload",
        headers={"Authorization": f"Basic {credentials}",},
        data=request_form,
    )
    assert post_response.status_code == 200


def test_submission_auth_dev_mode(
    rebuild_test_database,
    test_app_client_sql_backed_development_env,
    request_form,
    penguin_size_csv_file,
):
    # test the file upload when the app is running in wizard/development mode- no auth required
    client = test_app_client_sql_backed_development_env.test_client()
    get_response = client.get("/upload")
    assert get_response.status_code == 200
    request_form[CSVFILE] = penguin_size_csv_file

    post_response = client.post(
        "/upload", data=request_form, content_type="multipart/form-data"
    )
    # test post responses in dev- no auth required
    assert post_response.status_code == 200


def test_submission_validates_and_writes_to_db(
    rebuild_test_database,
    test_app_client_sql_backed_development_env,
    request_form,
    penguin_size_csv_file,
):
    request_form[CSVFILE] = penguin_size_csv_file
    # upload_ids = PenguinSize.upload_id.all_()
    session = test_app_client_sql_backed_development_env.db_session
    client = test_app_client_sql_backed_development_env.test_client()
    db_response = session.query(PenguinSize.upload_id).distinct()
    upload_ids_in_db = sorted([x.upload_id for x in db_response])

    expected_upload_ids = [1, 2]
    assert upload_ids_in_db == expected_upload_ids

    # check after a post with a new file that we have written to the db
    post_response = client.post(
        "/upload", data=request_form, content_type="multipart/form-data"
    )
    assert post_response.status_code == 200
    db_response = session.query(PenguinSize.upload_id).distinct()
    upload_ids_in_db = sorted([x.upload_id for x in db_response])
    expected_upload_ids = [1, 2, 3]
    assert [x for x in upload_ids_in_db] == expected_upload_ids
