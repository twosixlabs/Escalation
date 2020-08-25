# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import copy

from flask import current_app, render_template, Blueprint, request

from utility.constants import DATA_SOURCES, DATA_SOURCE_TYPE, MAIN_DATA_SOURCE

ADMIN_HTML = "admin.html"
INACTIVE = "inactive"
ACTIVE = "active"
admin_blueprint = Blueprint("admin", __name__)


@admin_blueprint.route("/admin", methods=("GET",))
def admin_page():
    data_inventory = current_app.config.data_backend_writer
    existing_data_sources = data_inventory.get_available_data_sources()
    data_sources = sorted(existing_data_sources)
    data_source_dict = {
        data_source: data_inventory(
            {MAIN_DATA_SOURCE: {DATA_SOURCE_TYPE: data_source}}
        ).get_identifiers_for_data_source()
        for data_source in data_sources
    }
    data_source_active_dict = copy.deepcopy(data_source_dict)
    data_source_active_dict.update(current_app.config.active_data_source_filters)
    return render_template(
        ADMIN_HTML,
        data_source_dict=data_source_dict,
        data_source_active_dict=data_source_active_dict,
    )


@admin_blueprint.route("/admin", methods=("POST",))
def submission():
    active_data_dict = request.form.to_dict()
    data_source_name = active_data_dict.pop(DATA_SOURCES)
    if INACTIVE in active_data_dict.values():
        current_app.config.active_data_source_filters.update(
            {
                data_source_name: [
                    identifier
                    for (identifier, active_state) in active_data_dict.items()
                    if active_state == ACTIVE
                ]
            }
        )
    else:
        current_app.config.active_data_source_filters.pop(data_source_name, [])
    return admin_page()
