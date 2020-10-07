# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import json

from flask import current_app, render_template, Blueprint, request

from controller import get_metadata
from utility.constants import DATA_SOURCES, UPLOAD_ID

ADMIN_HTML = "view_uploaded_data.html"

admin_blueprint = Blueprint("admin", __name__)


@admin_blueprint.route("/admin", methods=("GET",))
def admin_page():
    data_source_dict = get_metadata()
    return render_template(ADMIN_HTML, data_source_dict=data_source_dict, admin=True)


@admin_blueprint.route("/admin", methods=("POST",))
def submission():
    active_data_dict = request.form.to_dict()
    data_source_name = active_data_dict.pop(DATA_SOURCES)
    data_inventory = current_app.config.data_backend_writer
    data_inventory.update_data_upload_metadata_active(
        data_source_name, active_data_dict
    )
    return admin_page()
