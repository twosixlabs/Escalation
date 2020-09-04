# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import json

from flask import current_app, render_template, Blueprint, request

from utility.constants import DATA_SOURCES, UPLOAD_ID

ADMIN_HTML = "admin.html"

admin_blueprint = Blueprint("admin", __name__)


@admin_blueprint.route("/admin", methods=("GET",))
def admin_page():
    data_inventory = current_app.config.data_backend_writer
    existing_data_sources = data_inventory.get_available_data_sources()
    data_sources = sorted(existing_data_sources)
    data_source_dict = data_inventory.get_data_upload_metadata(data_sources)
    # this allows the dictionary to work with bootstrap-table with html form as a post request.
    data_source_dict = {
        data_source: {
            "ids": [element[UPLOAD_ID] for element in identifiers_metadata_dict_list],
            "data": json.dumps(identifiers_metadata_dict_list),
        }
        for data_source, identifiers_metadata_dict_list in data_source_dict.items()
    }
    return render_template(ADMIN_HTML, data_source_dict=data_source_dict)


@admin_blueprint.route("/admin", methods=("POST",))
def submission():
    active_data_dict = request.form.to_dict()
    data_source_name = active_data_dict.pop(DATA_SOURCES)
    print(active_data_dict)
    data_inventory = current_app.config.data_backend_writer
    data_inventory.update_data_upload_metadata_active(
        data_source_name, active_data_dict
    )
    return admin_page()
