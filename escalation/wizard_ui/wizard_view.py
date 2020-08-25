# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import json
import os

from flask import current_app, render_template, Blueprint, request

from utility.build_plotly_schema import SELECTOR_DICT

from utility.constants import (
    DATA_BACKEND,
    LOCAL_CSV,
    APP_CONFIG_JSON,
    AVAILABLE_PAGES,
    PAGE_ID,
    GRAPHIC,
    CONFIG_FILE_FOLDER,
    CONFIG_DICT,
    GRAPHIC_STATUS,
    GRAPHIC_CONFIG_FILES,
    WEBPAGE_LABEL,
    URL_ENDPOINT,
    DATABASE,
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
)

from wizard_ui.schemas_for_ui import (
    build_main_schemas_for_ui,
    build_graphic_schemas_for_ui,
    BACKEND_TYPES,
)
from wizard_ui.wizard_utils import (
    load_graphic_config_dict,
    save_main_config_dict,
    set_up_backend_for_wizard,
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

GRAPHIC_CONFIG_EDITOR_HTML = "graphic_config_editor.html"
MAIN_CONFIG_EDITOR_HTML = "main_config_editor.html"
CONFIG_FILES_HTML = "config_files.html"
wizard_blueprint = Blueprint("wizard", __name__)


@wizard_blueprint.route("/", methods=("GET",))
def file_tree():
    config_dict = load_main_config_dict_if_exists(current_app)
    inverted_backend_types = invert_dict_lists(BACKEND_TYPES)
    return render_template(
        CONFIG_FILES_HTML,
        available_pages=get_layout_for_dashboard(config_dict.get(AVAILABLE_PAGES, {})),
        current_config=config_dict,
        # load in the right schema based on the config dict, default to database
        current_schema=inverted_backend_types.get(
            config_dict.get(DATA_BACKEND, POSTGRES), DATABASE
        ),
    )


@wizard_blueprint.route("/", methods=("POST",))
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
        page_dict = {
            WEBPAGE_LABEL: webpage_label,
            URL_ENDPOINT: sanitize_string(
                webpage_label
            ),  # sanitizing the string so it is valid url
            GRAPHIC_CONFIG_FILES: [],
        }
        available_pages.append(page_dict)
    elif modification == DELETE_PAGE:
        del available_pages[int(request.form[PAGE_ID])]
    elif modification == DELETE_GRAPHIC:
        available_pages[int(request.form[PAGE_ID])][GRAPHIC_CONFIG_FILES].remove(
            request.form[GRAPHIC]
        )

    config_dict[AVAILABLE_PAGES] = available_pages
    save_main_config_dict(config_dict)
    return file_tree()


@wizard_blueprint.route("/main", methods=("GET",))
def main_config_setup():
    config_dict = load_main_config_dict_if_exists(current_app)
    inverted_backend_types = invert_dict_lists(BACKEND_TYPES)
    return render_template(
        MAIN_CONFIG_EDITOR_HTML,
        schema=json.dumps(build_main_schemas_for_ui()),
        current_config=json.dumps(config_dict),
        # load in the right schema based on the config dict, default to database
        current_schema=inverted_backend_types.get(
            config_dict.get(DATA_BACKEND, POSTGRES), DATABASE
        ),
    )


@wizard_blueprint.route("/graphic", methods=("POST",))
def graphic_config_setup():
    graphic_status = request.form[GRAPHIC_STATUS]

    config_dict = load_main_config_dict_if_exists(current_app)
    copy_data_from_form_to_config(config_dict, request.form)
    save_main_config_dict(config_dict)
    active_data_source_names = None
    if graphic_status in [COPY, OLD]:
        graphic_dict = json.loads(load_graphic_config_dict(request.form[GRAPHIC]))
        active_data_source_names = extract_data_sources_from_config(graphic_dict)

    csv_flag = config_dict[DATA_BACKEND] == LOCAL_CSV
    data_source_names, possible_column_names = get_data_source_info(
        csv_flag, active_data_source_names
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
        schema_selector_dict=SELECTOR_DICT,
        current_schema=current_schema,
        graphic_path=request.form[GRAPHIC],
    )


@wizard_blueprint.route("/main/save", methods=("POST",))
def update_main_json_config_with_ui_changes():
    config_dict = request.get_json()
    if APP_CONFIG_JSON not in current_app.config:
        set_up_backend_for_wizard(config_dict, current_app)
    save_main_config_dict(config_dict)

    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@wizard_blueprint.route("/graphic/save", methods=("POST",))
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

    with open(
        os.path.join(current_app.config[CONFIG_FILE_FOLDER], graphic_filename), "w"
    ) as fout:
        json.dump(graphic_dict, fout, indent=4)

    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@wizard_blueprint.route("/graphic/update_schemas", methods=("POST",))
def get_updated_schemas():
    active_data_source_names = request.get_json()
    config_dict = load_main_config_dict_if_exists(current_app)
    csv_flag = config_dict[DATA_BACKEND] == LOCAL_CSV
    data_source_names, possible_column_names = get_data_source_info(
        csv_flag, active_data_source_names
    )
    graphic_schemas, schema_to_type = build_graphic_schemas_for_ui(
        data_source_names, possible_column_names
    )

    return (
        json.dumps(graphic_schemas, indent=4,),
        200,
        {"ContentType": "application/json"},
    )
