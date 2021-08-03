# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import pandas
from flask import current_app, render_template, Blueprint, request
import pandas as pd

from app_deploy_data.authentication import auth
from database.file_upload_transform_functions import FILE_UPLOAD_FUNCTION_MAPPING
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
        exception_message = f"Error validating upload form: {type(e)} {e.args}"
        raise ValidationError(exception_message)

    current_app.logger.info(f"POST {username} {data_source_name}")
    return username, data_source_name, request_files


def load_csvfile(csvfile) -> (str, pandas.DataFrame):
    """
    :param csvfile: request.file from flask for the uploaded file
    :return:
    """
    try:
        filename = csvfile.filename
        df = pd.read_csv(csvfile, sep=",", comment="#")
        return filename, df
    except Exception as e:
        exception_message = f"Error loading {filename}: {type(e)} {e.args}"
        raise ValidationError(exception_message)


def validate_submission_content(df, filename, data_source_schema):
    """
    This function validates the contents of an uplaoded file against the expected schema
    Raises ValidationError if the file does not have the correct format/data types
    :param data_source_schema: sqlalchemy columns to use for validation
    :return: pandas dataframe of the uploaded csv
    """
    try:
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


def apply_file_transforms(
    data_file_df: pandas.DataFrame, filename: str, data_source_name: str
):
    """
    In general Escalation has been built assuming that you're uploading files that are
    more or less ready for visualization.
    However, in some cases there are simple transforms that we'd like to apply to an
    uploaded file that can't easily be done at the visualization runtime.
    This function runs on every file that is uploaded, checks whether the filename
    matches the user-defined mapping dict of transform functions, and executes the
    functions if so.
    The user-defined mapping functions live in
    database/file_upload_transform_functions.py
    :param data_file_df: the uploaded csv read into a pandas dataframe
    :param filename: the name of the file uploaded
    :param data_source_name: matches what the user has entered in the "Data File Type"
    field in the upload form, and the name of the data source in the backend
    :return: data_file_df: the uploaded csv modified with any transform functions
    """
    transform_functions_for_data_source_name = FILE_UPLOAD_FUNCTION_MAPPING.get(
        data_source_name, []
    )
    for transform_function in transform_functions_for_data_source_name:
        try:
            data_file_df = transform_function(data_file_df)
        except Exception as e:
            _ = filename
            exception_message = f"Error applying transform function {transform_function.__name__} to file {filename}: {type(e)} {e.args}"
            raise ValidationError(exception_message)
    return data_file_df


def upload_page(
    template: str, success_text: str = None, validation_error_message: str = None
):
    """
    :param template: html template name to render
    :param success_text: string that if present, triggers a success popup on the HTML
    :param validation_error_message: string that if present, triggers a failure popup
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
            filename, df = load_csvfile(file)
            df = apply_file_transforms(df, filename, data_source_name)
            df = validate_submission_content(df, filename, data_source_schema)
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
