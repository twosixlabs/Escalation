# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from flask import current_app, render_template, Blueprint, request, jsonify
from io import BufferedReader
import pandas as pd

from app_deploy_data.authentication import auth
from utility.constants import (
    INDEX_COLUMN,
    UPLOAD_ID,
    DATA_SOURCE_TYPE,
    MAIN_DATA_SOURCE,
    TABLE_COLUMN_SEPARATOR,
    NOTES,
    USERNAME,
    DATA_SOURCE,
    CSVFILE,
)
from utility.exceptions import ValidationError

UPLOAD_HTML = "data_upload.html"

upload_blueprint = Blueprint("upload", __name__)


def validate_data_form(request_form, request_files):
    """
    We want to validate a submitted form whether it comes from the HTML page or an API
    request. This function checks the form values, not the content of the upload.
    :param request_form: flask request.form object
    :param request_files: flask request.files object
    :return: required fields
    """
    try:
        notes = request_form[
            NOTES
        ]  # require this field to be here, but no other checks
        username = request_form[USERNAME]
        data_source_name = request_form[DATA_SOURCE]
        csvfile = request_files[CSVFILE]
    except KeyError as e:
        raise ValidationError(e)

    current_app.logger.info(f"POST {username} {data_source_name}")
    return username, data_source_name, csvfile


def validate_submission_content(csvfile, data_source_schema):
    """
    This function validates the contents of an uplaoded file against the expected schema
    Raises ValidationError if the file does not have the correct format/data types
    :param csvfile: request.file from flask for the uploaded file
    :param data_source_schema: sqlalchemy columns to use for validation
    :return: pandas dataframe of the uploaded csv
    """
    try:
        df = pd.read_csv(csvfile, sep=",", comment="#")
        existing_column_names = {
            x.split(TABLE_COLUMN_SEPARATOR)[-1] for x in data_source_schema
        }
        # if we have added an index column on the backend, don't look for it in the data
        for app_added_column in [INDEX_COLUMN, UPLOAD_ID]:
            if app_added_column in existing_column_names:
                existing_column_names.remove(app_added_column)
        # all of the columns in the existing data source are specified in upload
        assert set(df.columns).issuperset(
            existing_column_names
        ), f"Upload missing expected columns {existing_column_names - set(df.columns)}"
        # todo: match data types
        # todo- additional file type specific content validation
    except (AssertionError, ValueError) as e:
        raise ValidationError(str(e))
    return df


def upload_page(success_text=None):
    data_inventory = current_app.config.data_backend_writer
    existing_data_sources = data_inventory.get_available_data_sources()
    data_sources = sorted(existing_data_sources)
    return render_template(
        UPLOAD_HTML, data_sources=data_sources, success_text=success_text
    )


@upload_blueprint.route("/upload", methods=("POST",))
@auth.login_required
def submission():
    try:
        # check the submission form
        username, data_source_name, csvfile = validate_data_form(
            request.form, request.files
        )
        notes = request.form.get(NOTES)

        # if the form of the submission is right, let's validate the content of the submitted file
        data_inventory = current_app.config.data_backend_writer(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source_name}}
        )
        data_handler_class = current_app.config.data_handler(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source_name}}
        )
        data_source_schema = data_handler_class.get_column_names_for_data_source()

        df = validate_submission_content(csvfile, data_source_schema)
        data_inventory.write_data_upload_to_backend(df, username, notes)
        # write upload history table record at the same time

    except ValidationError as e:
        current_app.logger.info(e, exc_info=True)
        # check if POST comes from script instead of web UI
        return jsonify({"error": str(e)}), 400

    # todo: log information about what the submission is
    current_app.logger.info("Added submission")
    return upload_page("Success")


@upload_blueprint.route("/upload", methods=("GET",))
def submission_view():
    return upload_page()
