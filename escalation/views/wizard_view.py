# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
from io import open as io_open
import json
import os
import re

from flask import current_app, render_template, Blueprint, request
import pandas as pd
from sqlacodegen.codegen import CodeGenerator

from controller import get_data_for_page
from database.sql_handler import CreateTablesFromCSVs, REPLACE, SqlDataInventory
from graphics.graphic_schema import GraphicsConfigInterfaceBuilder
from graphics.utils.available_graphics import (
    PLOT_DELIMITER,
    get_all_available_graphics,
    AVAILABLE_GRAPHICS,
)
from utility.constants import *
from utility.exceptions import ValidationError
from utility.wizard_utils import (
    load_graphic_config_dict,
    save_main_config_dict,
    load_main_config_dict_if_exists,
    sanitize_string,
    graphic_dict_to_graphic_component_dict,
    graphic_component_dict_to_graphic_dict,
    get_layout_for_dashboard,
    extract_data_sources_from_config,
    copy_data_from_form_to_config,
    make_page_dict_for_main_config,
    generate_collapse_dict_from_graphic_component_dict,
    get_default_collapse_dict,
)
from views.file_upload import upload_page


GRAPHIC_CONFIG_EDITOR_HTML = "wizard_graphic_config_editor.html"
CONFIG_FILES_HTML = "wizard_configurer.html"
CSV_TO_DATABASE_UPLOAD_HTML = "wizard_data_upload.html"
GRAPHIC_CONFIG_LANDING_PAGE = "wizard_config_landing_page.html"
wizard_blueprint = Blueprint("wizard", __name__)


@wizard_blueprint.route("/wizard/", methods=("GET",))
def file_tree():
    config_dict = load_main_config_dict_if_exists(current_app)
    return render_template(
        CONFIG_FILES_HTML,
        available_pages=get_layout_for_dashboard(config_dict.get(AVAILABLE_PAGES, {})),
        current_config=config_dict,
        # load in the right schema based on the config dict, default to database
        current_schema=config_dict.get(DATA_BACKEND, POSTGRES),
    )


@wizard_blueprint.route("/wizard/", methods=("POST",))
def modify_layout():
    """
    Add a page
    Delete a page
    Delete a graphic from a page
    :return:
    """
    MODIFICATION = "modification"
    ADD_PAGE = "add_page"
    DELETE_PAGE = "delete_page"
    RENAME_PAGE = "rename_page"
    DELETE_GRAPHIC = "delete_graphic"

    config_dict = load_main_config_dict_if_exists(current_app)
    copy_data_from_form_to_config(config_dict, request.form)
    available_pages = config_dict.get(AVAILABLE_PAGES, [])
    modification = request.form[MODIFICATION]
    webpage_label = request.form[WEBPAGE_LABEL]
    page_id = int(request.form[PAGE_ID])
    if modification == ADD_PAGE:
        page_urls = [page_dict[URL_ENDPOINT] for page_dict in available_pages]
        page_dict = make_page_dict_for_main_config(webpage_label, page_urls)
        available_pages.append(page_dict)
    elif modification == RENAME_PAGE:
        page_urls = [page_dict[URL_ENDPOINT] for page_dict in available_pages]
        page_urls.pop(page_id)
        page_dict = make_page_dict_for_main_config(webpage_label, page_urls)
        page_dict[GRAPHIC_CONFIG_FILES] = available_pages[page_id].get(
            GRAPHIC_CONFIG_FILES, []
        )
        available_pages[page_id] = page_dict
    elif modification == DELETE_PAGE:
        del available_pages[page_id]
        # todo: iterate and delete actual json configs? But add confirmation?
    elif modification == DELETE_GRAPHIC:
        graphic_filename = request.form[GRAPHIC]
        graphic_filepath = os.path.join(
            current_app.config[CONFIG_FILE_FOLDER], graphic_filename
        )
        # remove and write new file to trigger file watcher and refresh flask app
        if os.path.exists(graphic_filepath):
            os.remove(graphic_filepath)
        available_pages[page_id][GRAPHIC_CONFIG_FILES].remove(graphic_filename)

    config_dict[AVAILABLE_PAGES] = available_pages
    save_main_config_dict(config_dict)
    return file_tree()


@wizard_blueprint.route("/wizard/graphic/landing", methods=("POST",))
def graphic_landing_setup():
    return render_template(
        GRAPHIC_CONFIG_LANDING_PAGE,
        page_id=request.form[PAGE_ID],
        graphic_status=request.form[GRAPHIC_STATUS],
        graphic_path=request.form[GRAPHIC],
        plot_dict=get_all_available_graphics(),
        data_source_schema=json.dumps(
            GraphicsConfigInterfaceBuilder.get_wizard_data_source_schema()
        ),
    )


@wizard_blueprint.route("/wizard/graphic/config", methods=("POST",))
def graphic_config_setup():
    graphic_status = request.form[GRAPHIC_STATUS]
    graphic_dict = {}

    collapse_dict = get_default_collapse_dict()
    if graphic_status in [COPY, OLD]:
        graphic_dict = json.loads(load_graphic_config_dict(request.form[GRAPHIC]))
        plot_manager = graphic_dict[PLOT_MANAGER]
        plot_type = graphic_dict[PLOT_TYPE]
        collapse_dict = generate_collapse_dict_from_graphic_component_dict(graphic_dict)
    else:
        plot_manager, plot_type = request.form[PLOT_TYPE].split(PLOT_DELIMITER)
        graphic_dict[PLOT_MANAGER] = plot_manager
        graphic_dict[PLOT_TYPE] = plot_type
        graphic_dict[DATA_SOURCES] = json.loads(request.form[DATA_SOURCES])
    active_data_source_names = extract_data_sources_from_config(graphic_dict)
    kwargs = {
        "active_data_source_names": active_data_source_names,
        "collapse_dict": collapse_dict,
    }
    plot_info = AVAILABLE_GRAPHICS[plot_manager]
    if plot_manager in PLOT_MANAGERS:
        graphic_config = plot_info[SCHEMA_CLASS](**kwargs)
    else:
        raise ValueError(f"plot_manager {plot_manager} not recognized")

    ui_formatted_schema = graphic_config.build_graphic_schemas_for_ui(plot_type)
    component_graphic_dict = graphic_dict_to_graphic_component_dict(graphic_dict)
    return render_template(
        GRAPHIC_CONFIG_EDITOR_HTML,
        # todo: rename 'schema'
        schema=json.dumps(ui_formatted_schema, indent=4,),
        page_id=request.form[PAGE_ID],
        current_config=json.dumps(component_graphic_dict),
        graphic_status=graphic_status,
        schema_selector_dict=json.dumps(graphic_config.plot_selector_dict),
        graphic_path=request.form[GRAPHIC],
        default_entries_dict=json.dumps(graphic_config.unique_entries_dict),
        graph_html_template=plot_info[OBJECT].get_graph_html_template(),
    )


@wizard_blueprint.route("/wizard/main/save", methods=("POST",))
def update_main_json_config_with_ui_changes():
    config_dict = request.get_json()
    save_main_config_dict(config_dict)
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@wizard_blueprint.route("/wizard/graphic/save", methods=("POST",))
def update_graphic_json_config_with_ui_changes():
    config_information_dict = request.get_json()
    page_id = config_information_dict[PAGE_ID]
    graphic_dict = graphic_component_dict_to_graphic_dict(
        config_information_dict[CONFIG_DICT]
    )
    graphic_filename = config_information_dict[GRAPHIC_PATH]
    # sanitizing the string so it is valid filename
    if config_information_dict[GRAPHIC_STATUS] in [NEW, COPY]:
        # Given a graphic title from the user input, make a valid json filename
        graphic_filename_no_ext = sanitize_string(graphic_dict[GRAPHIC_TITLE])
        if os.path.exists(
            os.path.join(
                current_app.config[CONFIG_FILE_FOLDER],
                f"{graphic_filename_no_ext}.json",
            )
        ):
            i = 0
            while os.path.exists(
                os.path.join(
                    current_app.config[CONFIG_FILE_FOLDER],
                    f"{graphic_filename_no_ext}_{i}.json",
                )
            ):
                i += 1
            graphic_filename = f"{graphic_filename_no_ext}_{i}.json"
        else:
            graphic_filename = f"{graphic_filename_no_ext}.json"
        # make sure we are not overwriting something
        main_config_dict = load_main_config_dict_if_exists(current_app)
        page_dict = main_config_dict[AVAILABLE_PAGES][page_id]
        graphic_list = page_dict.get(GRAPHIC_CONFIG_FILES, [])
        graphic_list.append(graphic_filename)
        page_dict[GRAPHIC_CONFIG_FILES] = graphic_list
        save_main_config_dict(main_config_dict)

    graphic_filepath = os.path.join(
        current_app.config[CONFIG_FILE_FOLDER], graphic_filename
    )
    # remove and write new file to trigger file watcher and refresh flask app
    if os.path.exists(graphic_filepath):
        os.remove(graphic_filepath)
    with open(graphic_filepath, "w") as fout:
        json.dump(graphic_dict, fout, indent=4)
    return (
        json.dumps({"success": True, GRAPHIC_PATH: graphic_filename}),
        200,
        {"ContentType": "application/json"},
    )


@wizard_blueprint.route("/wizard/graphic/preview", methods=("POST",))
def preview_graphic_json_config():
    config_information_dict = request.get_json()
    graphic_dict = graphic_component_dict_to_graphic_dict(
        config_information_dict[CONFIG_DICT]
    )
    # get_data_for_page needs a graphic label
    plot_specs = get_data_for_page({PREVIEW: graphic_dict})
    # plot_specs is more nested than we want for the preveiw so get the plot_dict and pass that to the html
    return (
        json.dumps({"success": True, PREVIEW: plot_specs[0][JINJA_PLOT_INFO]}),
        200,
        {"ContentType": "application/json"},
    )


@wizard_blueprint.route("/wizard/upload", methods=("GET",))
def data_upload_page_view():
    return upload_page(template=CSV_TO_DATABASE_UPLOAD_HTML)


def validate_table_name(table_name: str):
    """
    ensures that a user-entered table name is supported by Postgres
    """
    # todo: check there is any name at all?
    if not re.match(POSTGRES_TABLE_NAME_FORMAT_REGEX, table_name):
        message = (
            f"Check formatting of {table_name}"
            "Table names name must start with a letter or an underscore; "
            "the rest of the string can contain letters, digits, and underscores."
        )
    elif len(table_name) > 31:
        message = f"Table name {table_name} too long. Postgres SQL only supports table names with length <= 31"
    elif re.match("[A-Z]", table_name):
        # sanitize_string now silently lowercases in background-
        # this is currently not reachable
        message = (
            "Postgres SQL table names are case insensitive- "
            "please use only lowercase letters"
        )
    else:
        # there are no validation issues
        return
    raise ValidationError(message)


def validate_wizard_upload_submission(
    table_name: str, csvfiles, csv_sql_creator: CreateTablesFromCSVs
):
    """
    Checks that the name of the uploaded table is valid,
    and in the case of multiple uploaded files, that the schemas agree.
    Raises ValidationError on any problems
    :param table_name: sanitized flask form string
    :param csvfiles: flask request files list
    :param csv_sql_creator: CreateTablesFromCSVs instance
    :return: combined dataframe from multiple files.
    """
    validate_table_name(table_name)
    data_file_schemas = None
    # for each file in the uploaded list of files,
    #  assert that the columns contained are the same name and datatype
    dfs = []
    mismatches = []

    for csvfile in csvfiles:
        data = csv_sql_creator.get_data_from_csv(csvfile)
        df, schema = csv_sql_creator.get_schema_from_df(data)
        if not data_file_schemas:
            data_file_schemas = schema
            base_schema_file = csvfile.filename
        else:
            # raise error if column names don't match
            if set(schema) - set(data_file_schemas):
                mismatch_columns = f"columns in {csvfile.filename} not in {base_schema_file}: {set(schema) - set(data_file_schemas)}"
                mismatches.append(mismatch_columns)
            if set(data_file_schemas) - set(schema):
                mismatch_columns = f"columns in {base_schema_file} not in {csvfile.filename}: {set(data_file_schemas) - set(schema)}"
                mismatches.append(mismatch_columns)
            # raise error if column types don't match
            for column_name, column_type in schema.items():
                if (
                    column_name in data_file_schemas
                    and data_file_schemas[column_name] != column_type
                ):
                    mismatches.append(
                        f"Data type mismatch: {column_name}: {base_schema_file}:{data_file_schemas[column_name].__name__} and {csvfile.filename}:{column_type.__name__}"
                    )
        if len(mismatches) > 0:
            raise ValidationError(
                f"The following columns are inconsistent- upload failed: {mismatches}"
            )
        dfs.append(df)
    return pd.concat(dfs).reset_index(drop=True)


# todo: move to file_upload.py
def sql_backend_file_to_table_upload(upload_form, csvfiles):
    """

    :param upload_form: flask request form
    :param csvfiles: flask request files list
    :return: None. Raises a validation error if there are problems with the formatting
    """
    table_name = sanitize_string(upload_form.get(DATA_SOURCE))
    username = upload_form.get(USERNAME)
    notes = upload_form.get(NOTES)

    csv_sql_creator = CreateTablesFromCSVs(current_app.config[SQLALCHEMY_DATABASE_URI])
    data = validate_wizard_upload_submission(
        table_name=table_name, csvfiles=csvfiles, csv_sql_creator=csv_sql_creator
    )
    (
        upload_id,
        upload_time,
        table_name,
    ) = csv_sql_creator.create_and_fill_new_sql_table_from_df(table_name, data, REPLACE)

    # remove any existing metadata for this table name and write a new row
    SqlDataInventory.remove_metadata_rows_for_table_name(table_name)
    SqlDataInventory.write_upload_metadata_row(
        upload_id=upload_id,
        upload_time=upload_time,
        table_name=table_name,
        active=True,
        username=username,
        notes=notes,
    )
    # Generate a new models.py
    # update the metadata to include all tables in the db
    csv_sql_creator.meta.reflect()
    # write the database schema to models.py
    generator = CodeGenerator(csv_sql_creator.meta, noinflect=True)
    # Write the generated model code to the specified file or standard output
    models_filepath = os.path.join(APP_DEPLOY_DATA, "models.py")
    # remove and write new file to trigger file watcher and refresh flask app
    if os.path.exists(models_filepath):
        os.remove(models_filepath)
    with io_open(os.path.join(models_filepath), "w", encoding="utf-8") as outfile:
        generator.render(outfile)


@wizard_blueprint.route("/wizard/upload", methods=("POST",))
def upload_csv_to_database():
    upload_form = request.form
    csvfiles = request.files.getlist(CSVFILE)
    data_backend = current_app.config[APP_CONFIG_JSON].get(DATA_BACKEND)
    if data_backend in [POSTGRES]:
        try:
            sql_backend_file_to_table_upload(upload_form, csvfiles)
        except ValidationError as e:
            current_app.logger.info(e, exc_info=True)
            return (
                upload_page(
                    template=CSV_TO_DATABASE_UPLOAD_HTML,
                    validation_error_message=str(e),
                ),
                400,
            )

    else:
        return (
            upload_page(
                template=CSV_TO_DATABASE_UPLOAD_HTML,
                validation_error_message="Failure- data backend not recognized",
            ),
            400,
        )
    return upload_page(template=CSV_TO_DATABASE_UPLOAD_HTML, success_text="success")
