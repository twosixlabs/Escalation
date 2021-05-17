# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from flask import current_app, render_template, Blueprint, request
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
        # todo: validate file types in request_files
    except KeyError as e:
        raise ValidationError(e)

    current_app.logger.info(f"POST {username} {data_source_name}")
    return username, data_source_name, request_files


def validate_submission_content(csvfile, data_source_schema):
    """
    This function validates the contents of an uplaoded file against the expected schema
    Raises ValidationError if the file does not have the correct format/data types
    :param csvfile: request.file from flask for the uploaded file
    :param data_source_schema: sqlalchemy columns to use for validation
    :return: pandas dataframe of the uploaded csv
    """
    try:
        filename = csvfile.filename
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
        ), f"Upload {filename} missing expected columns {existing_column_names - set(df.columns)}"
        # todo: match data types
        # todo- additional file type specific content validation
    except (AssertionError, ValueError) as e:
        raise ValidationError(str(e))
    return df


def get_data_sources():
    data_inventory = current_app.config.data_backend_writer
    existing_data_sources = data_inventory.get_available_data_sources()
    return sorted(existing_data_sources)


def upload_page(
    template: str, success_text: str = None, validation_error_message: str = None
):
    """
    :param template: html template name to render
    :param success_text: string that if present, triggers a success popup on the HTML
    :param validation_error_message: string that if present, triggers a failuire popup
    on the HTML
    :return: jinja rendered template
    """
    data_sources = get_data_sources()
    alert_flag = {}
    # include at most one success or failure message for rendering on template
    if success_text:
        alert_flag["success_text"] = success_text
    elif validation_error_message:
        alert_flag["failure_text"] = validation_error_message
    return render_template(template, data_sources=data_sources, **alert_flag)


@upload_blueprint.route("/upload", methods=("POST",))
@auth.login_required
def submission():
    try:
        # check the submission form
        files = request.files.getlist(CSVFILE)
        username, data_source_name, csvfiles = validate_data_form(request.form, files)
        notes = request.form.get(NOTES)

        # if the form of the submission is right, let's validate the content of the submitted file
        data_inventory = current_app.config.data_backend_writer(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source_name}}
        )
        data_handler_class = current_app.config.data_handler(
            data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source_name}}
        )
        data_source_schema = data_handler_class.get_column_names_for_data_source()

        # validate each uploaded file before writing any to db
        dfs = []
        for file in files:
            df = validate_submission_content(file, data_source_schema)
            dfs.append(df)
        # by combining dfs before upload we get a single upload_id and metadata write
        df = pd.concat(dfs).reset_index(drop=True)
        data_inventory.write_data_upload_to_backend(df, username, notes)
        # write upload history table record at the same time

    except ValidationError as e:
        current_app.logger.info(e, exc_info=True)
        # return bad request code with a rendered template
        return upload_page(template=UPLOAD_HTML, validation_error_message=str(e)), 400
        # todo: check if POST comes from script instead of web UI and return json
        # return jsonify({"error": str(e)}), 400

    # todo: log information about what the submission is
    current_app.logger.info("Added submission")
    return upload_page(template=UPLOAD_HTML, success_text="Success")


@upload_blueprint.route("/upload", methods=("GET",))
def submission_view():
    return upload_page(template=UPLOAD_HTML)
