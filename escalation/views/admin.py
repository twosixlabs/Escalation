# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from flask import current_app, render_template, Blueprint, request


from controller import get_datasource_metadata_formatted_for_admin_panel
from utility.constants import DATA_SOURCES
from app_deploy_data.authentication import auth


ADMIN_HTML = "view_uploaded_data.html"

admin_blueprint = Blueprint("admin", __name__)


@admin_blueprint.route("/admin", methods=("GET",))
@auth.login_required
def admin_page():
    data_source_dict = get_datasource_metadata_formatted_for_admin_panel()
    return render_template(ADMIN_HTML, data_source_dict=data_source_dict, admin=True)


@admin_blueprint.route("/admin", methods=("POST",))
@auth.login_required
def submission():
    active_data_dict = request.form.to_dict()
    data_source_name = active_data_dict.pop(DATA_SOURCES)
    data_inventory = current_app.config.data_backend_writer
    data_inventory.update_data_upload_metadata_active(
        data_source_name, active_data_dict
    )
    return admin_page()
