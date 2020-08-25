# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from flask import current_app, render_template, Blueprint, request, jsonify, flash
import pandas as pd

from utility.constants import (
    INDEX_COLUMN,
    UPLOAD_ID,
    DATA_SOURCE_TYPE,
)

UPLOAD_HTML = "data_upload.html"

upload_blueprint = Blueprint("upload", __name__)


class ValidationError(Exception):
    """
    Exception class for when an Escalation validation step fails.
    This is a catchall for many Python exceptions that correspond to bad file contents
    """

    pass


def validate_data_form(request_form, request_files):
    """
    We want to validate a submitted form whether it comes from the HTML page or an API
    request. This function checks the form values, not the content of the upload.
    :param request_form: flask request.form object
    :param request_files: flask request.files object
    :return: required fields
    """
    for key in ("username", "data_source", "notes"):
        if key not in request_form:
            raise ValidationError("Key %s not present in POST" % key)
    try:
        username = request_form["username"]
        data_source_name = request_form["data_source"]
        csvfile = request_files["csvfile"]
    # todo: validate upload filename with secure_filename, sql table name validator
    except KeyError:
        raise ValidationError
    current_app.logger.info(f"POST {username} {data_source_name} {csvfile.filename}")
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
        existing_column_names = set([x.name for x in data_source_schema])
        # if we have added an index column on the backend, don't look for it in the data
        for app_added_column in [INDEX_COLUMN, UPLOAD_ID]:
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


@upload_blueprint.route("/upload", methods=("GET",))
def submission_view():
    data_inventory = current_app.config.data_backend_writer
    existing_data_sources = data_inventory.get_available_data_sources()
    data_sources = sorted(existing_data_sources)
    return render_template(UPLOAD_HTML, data_sources=data_sources)


@upload_blueprint.route("/upload", methods=("POST",))
def submission():
    try:
        # check the submission form
        username, data_source_name, csvfile = validate_data_form(
            request.form, request.files
        )
        # if the form of the submission is right, let's validate the content of the submitted file
        data_inventory = current_app.config.data_backend_writer(
            data_sources=[{DATA_SOURCE_TYPE: data_source_name}]
        )
        data_source_schema = data_inventory.get_schema_for_data_source()
        df = validate_submission_content(csvfile, data_source_schema)
        # write upload history table record at the same time
        ignored_columns = data_inventory.write_data_upload_to_backend(df)
    except ValidationError as e:
        current_app.logger.info(e, exc_info=True)
        # check if POST comes from script instead of web UI
        return jsonify({"error": e}), 400

    # todo: log information about what the submission is
    current_app.logger.info("Added submission")
    return render_template(
        "success.html", username="username", ignored_columns=ignored_columns
    )
