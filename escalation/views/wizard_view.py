# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from io import open as io_open
import json
import os

from flask import current_app, render_template, Blueprint, request
from sqlacodegen.codegen import CodeGenerator

from database.sql_handler import CreateTablesFromCSVs, REPLACE, SqlDataInventory
from database.local_handler import LocalCSVHandler, LocalCSVDataInventory
from utility.build_plotly_schema import SELECTOR_DICT
from utility.constants import (
    DATA_BACKEND,
    AVAILABLE_PAGES,
    PAGE_ID,
    GRAPHIC,
    CONFIG_FILE_FOLDER,
    CONFIG_DICT,
    GRAPHIC_STATUS,
    GRAPHIC_CONFIG_FILES,
    WEBPAGE_LABEL,
    URL_ENDPOINT,
    SCATTER,
    POSTGRES,
    DATA,
    TYPE,
    PLOT_SPECIFIC_INFO,
    COPY,
    OLD,
    NEW,
    GRAPHIC_PATH,
    GRAPHIC_TITLE,
    APP_DEPLOY_DATA,
    SQLALCHEMY_DATABASE_URI,
    USERNAME,
    NOTES,
    APP_CONFIG_JSON,
    MAIN_DATA_SOURCE,
    DATA_SOURCE_TYPE,
    LOCAL_CSV,
    DATA_SOURCE,
)
from utility.schemas_for_ui import build_graphic_schemas_for_ui
from utility.wizard_utils import (
    load_graphic_config_dict,
    save_main_config_dict,
    load_main_config_dict_if_exists,
    sanitize_string,
    invert_dict_lists,
    make_empty_component_dict,
    graphic_dict_to_graphic_component_dict,
    graphic_component_dict_to_graphic_dict,
    get_layout_for_dashboard,
    get_data_source_info,
    extract_data_sources_from_config,
    copy_data_from_form_to_config,
)

GRAPHIC_CONFIG_EDITOR_HTML = "wizard_graphic_config_editor.html"
CONFIG_FILES_HTML = "wizard_configurer.html"
CSV_TO_DATABASE_UPLOAD_HTML = "wizard_data_upload.html"
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
    DELETE_GRAPHIC = "delete_graphic"
    config_dict = load_main_config_dict_if_exists(current_app)
    copy_data_from_form_to_config(config_dict, request.form)
    available_pages = config_dict.get(AVAILABLE_PAGES, [])
    modification = request.form[MODIFICATION]
    if modification == ADD_PAGE:
        webpage_label = request.form[WEBPAGE_LABEL]
        page_urls = [page_dict[URL_ENDPOINT] for page_dict in available_pages]
        candidate_url = sanitize_string(
            webpage_label
        )  # sanitizing the string so it is valid url
        if candidate_url in page_urls:
            i = 0
            while f"{candidate_url}_{i}" in page_urls:
                i += 1
            candidate_url = f"{candidate_url}_{i}"

        page_dict = {
            WEBPAGE_LABEL: webpage_label,
            URL_ENDPOINT: candidate_url,
            GRAPHIC_CONFIG_FILES: [],
        }
        available_pages.append(page_dict)
    elif modification == DELETE_PAGE:
        del available_pages[int(request.form[PAGE_ID])]
        # todo: iterate and delete actual json configs? But add confirmation?
    elif modification == DELETE_GRAPHIC:
        graphic_filename = request.form[GRAPHIC]
        graphic_filepath = os.path.join(
            current_app.config[CONFIG_FILE_FOLDER], graphic_filename
        )
        # remove and write new file to trigger file watcher and refresh flask app
        if os.path.exists(graphic_filepath):
            os.remove(graphic_filepath)
        available_pages[int(request.form[PAGE_ID])][GRAPHIC_CONFIG_FILES].remove(
            graphic_filename
        )

    config_dict[AVAILABLE_PAGES] = available_pages
    save_main_config_dict(config_dict)
    return file_tree()


@wizard_blueprint.route("/wizard/graphic", methods=("POST",))
def graphic_config_setup():
    graphic_status = request.form[GRAPHIC_STATUS]

    config_dict = load_main_config_dict_if_exists(current_app)
    copy_data_from_form_to_config(config_dict, request.form)
    save_main_config_dict(config_dict)
    active_data_source_names = None
    if graphic_status in [COPY, OLD]:
        graphic_dict = json.loads(load_graphic_config_dict(request.form[GRAPHIC]))
        active_data_source_names = extract_data_sources_from_config(graphic_dict)

    data_source_names, possible_column_names = get_data_source_info(
        active_data_source_names
    )
    graphic_schemas, schema_to_type = build_graphic_schemas_for_ui(
        data_source_names, possible_column_names
    )
    component_graphic_dict = make_empty_component_dict()
    current_schema = SCATTER

    if graphic_status in [COPY, OLD]:
        type_to_schema = invert_dict_lists(schema_to_type)
        current_schema = type_to_schema[
            graphic_dict[PLOT_SPECIFIC_INFO][DATA][0].get(TYPE, SCATTER)
        ]
        component_graphic_dict = graphic_dict_to_graphic_component_dict(graphic_dict)

    return render_template(
        GRAPHIC_CONFIG_EDITOR_HTML,
        schema=json.dumps(graphic_schemas, indent=4,),
        page_id=request.form[PAGE_ID],
        current_config=json.dumps(component_graphic_dict),
        graphic_status=graphic_status,
        schema_selector_dict=json.dumps(SELECTOR_DICT),
        current_schema=current_schema,
        graphic_path=request.form[GRAPHIC],
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
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@wizard_blueprint.route("/wizard/graphic/update_schemas", methods=("POST",))
def get_updated_schemas():
    active_data_source_names = request.get_json()
    data_source_names, possible_column_names = get_data_source_info(
        active_data_source_names
    )
    graphic_schemas, schema_to_type = build_graphic_schemas_for_ui(
        data_source_names, possible_column_names
    )

    return (
        json.dumps(graphic_schemas, indent=4,),
        200,
        {"ContentType": "application/json"},
    )


def data_upload_page(success_text=None):
    data_inventory_class = current_app.config.data_backend_writer
    data_source_names = data_inventory_class.get_available_data_sources()
    data_sources = sorted(data_source_names)
    return render_template(
        CSV_TO_DATABASE_UPLOAD_HTML,
        data_sources=data_sources,
        success_text=success_text,
    )


@wizard_blueprint.route("/wizard/upload", methods=("GET",))
def data_upload_page_view():
    return data_upload_page()


def validate_table_name():
    # todo: form validate table name, but in js for pre-submit warning?
    # POSTGRES_TABLE_NAME_FORMAT_REGEX = r"^[a-zA-Z_]\w+$"
    # if not re.match(POSTGRES_TABLE_NAME_FORMAT_REGEX, table_name):
    #     print(
    #         "Table names name must start with a letter or an underscore;"
    #         " the rest of the string can contain letters, digits, and underscores."
    #     )
    #     exit(1)
    # if len(table_name) > 31:
    #     print(
    #         "Postgres SQL only supports table names with length <= 31-"
    #         " additional characters will be ignored"
    #     )
    #     exit(1)
    # if re.match("[A-Z]", table_name):
    #     print(
    #         "Postgres SQL table names are case insensitive- "
    #         "tablename will be converted to lowercase letters"
    #     )
    #
    pass


def sql_backend_file_upload(upload_form, csvfile):
    table_name = upload_form.get(DATA_SOURCE)
    username = upload_form.get(USERNAME)
    notes = upload_form.get(NOTES)
    csv_sql_writer = CreateTablesFromCSVs(current_app.config[SQLALCHEMY_DATABASE_URI])
    data = csv_sql_writer.get_data_from_csv(csvfile)
    (
        upload_id,
        upload_time,
        table_name,
    ) = csv_sql_writer.create_and_fill_new_sql_table_from_df(table_name, data, REPLACE)

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
    csv_sql_writer.meta.reflect()
    # write the database schema to models.py
    generator = CodeGenerator(csv_sql_writer.meta, noinflect=True)
    # Write the generated model code to the specified file or standard output
    models_filepath = os.path.join(APP_DEPLOY_DATA, "models.py")
    # remove and write new file to trigger file watcher and refresh flask app
    if os.path.exists(models_filepath):
        os.remove(models_filepath)
    with io_open(os.path.join(models_filepath), "w", encoding="utf-8") as outfile:
        generator.render(outfile)


def csv_backend_file_upload(upload_form, csvfile):
    table_name = upload_form.get(DATA_SOURCE)
    username = upload_form.get(USERNAME)
    notes = upload_form.get(NOTES)
    df = LocalCSVHandler.load_df_from_csv(csvfile)
    data_inventory = LocalCSVDataInventory(
        data_sources={MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: table_name}}
    )
    data_inventory.delete_data_source()
    data_inventory.write_data_upload_to_backend(
        uploaded_data_df=df, filename=csvfile.filename, username=username, notes=notes
    )


@wizard_blueprint.route("/wizard/upload", methods=("POST",))
def upload_csv_to_database():
    upload_form = request.form
    csvfile = request.files.get("csvfile")
    data_backend = current_app.config[APP_CONFIG_JSON].get(DATA_BACKEND)
    if data_backend in [POSTGRES]:
        sql_backend_file_upload(upload_form, csvfile)
    elif data_backend in [LOCAL_CSV]:
        csv_backend_file_upload(upload_form, csvfile)
    else:
        return data_upload_page("Failure- data backend not recognized")
    return data_upload_page("success")
