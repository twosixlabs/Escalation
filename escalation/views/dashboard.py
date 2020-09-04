# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

from flask import current_app, render_template, Blueprint, request
from werkzeug.exceptions import BadRequest

from utility.constants import (
    APP_CONFIG_JSON,
    PROCESS,
    SITE_TITLE,
    SITE_DESC,
    AVAILABLE_PAGES_DICT,
    JINJA_PLOT,
    CURRENT_PAGE,
)
from controller import get_data_for_page


DATA_LAYOUT = "data_layout.html"

dashboard_blueprint = Blueprint("dashboard", __name__)


@dashboard_blueprint.route("/dashboard/")
@dashboard_blueprint.route("/")
def main_page():
    return render_template(DATA_LAYOUT)


@dashboard_blueprint.route("/dashboard/<page_name>", methods=["GET", "POST"])
def graphic_page(page_name):
    try:
        html_data_list = get_data_for_page(
            single_page_config_dict=current_app.config.get(AVAILABLE_PAGES_DICT).get(
                page_name
            ),
            # request.form[PROCESS]=='' means the reset button sent the request
            addendum_dict=request.form
            if request.form and request.form[PROCESS]
            else None,
        )
    # This can happen during app configuration in the wizard, when refresh POSTS don't
    # match the expected format. Retry the render as if there were no POST data
    except BadRequest:
        html_data_list = get_data_for_page(
            single_page_config_dict=current_app.config.get(AVAILABLE_PAGES_DICT).get(
                page_name
            ),
            addendum_dict=None,
        )
    return render_template(
        DATA_LAYOUT, **{CURRENT_PAGE: page_name, JINJA_PLOT: html_data_list}
    )


@dashboard_blueprint.context_processor
def create_jumbotron_info():
    config_dict = current_app.config.get(APP_CONFIG_JSON)
    jumbotron_info = {
        SITE_TITLE: config_dict.get(SITE_TITLE, ""),
        SITE_DESC: config_dict.get(SITE_DESC, ""),
    }
    return jumbotron_info
