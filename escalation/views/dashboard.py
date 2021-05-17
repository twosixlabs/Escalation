# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0
import json

from flask import current_app, render_template, Blueprint, request, make_response
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import BadRequest

from utility.constants import (
    APP_CONFIG_JSON,
    PROCESS,
    SITE_TITLE,
    SITE_DESC,
    AVAILABLE_PAGES_DICT,
    JINJA_PLOT,
    CURRENT_PAGE,
    ADDENDUM_DICT,
    DEVELOPMENT,
    GRAPHIC_NAME,
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
    """
    We store the user settings as a cookie in ADDENDUM_DICT
    When a post request is sent, We modify the cookie
    with the form submission of new filters.
    :param page_name:
    :return:
    """
    # Do not read in cookies in development mode
    if current_app.config.get("ENV") != DEVELOPMENT:
        addendum_dict = json.loads(request.cookies.get(ADDENDUM_DICT, "{}"))
    else:
        addendum_dict = {}
    if request.form:
        # request.form[PROCESS]=='' means the reset button sent the request
        if request.form[PROCESS]:
            add_form_to_addendum_dict(request.form, addendum_dict)
        else:
            addendum_dict = {}
    try:
        html_data_list = get_data_for_page(
            single_page_config_dict=current_app.config.get(AVAILABLE_PAGES_DICT).get(
                page_name
            ),
            addendum_dict=addendum_dict,
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
    resp = make_response(
        render_template(
            DATA_LAYOUT, **{CURRENT_PAGE: page_name, JINJA_PLOT: html_data_list}
        )
    )
    # we're attaching a cookie tracking the state of the filters to the rendered template response.
    # Do not write cookies in development mode
    if current_app.config.get("ENV") != DEVELOPMENT:
        resp.set_cookie(ADDENDUM_DICT, json.dumps(addendum_dict))
    return resp


@dashboard_blueprint.context_processor
def create_jumbotron_info():
    config_dict = current_app.config.get(APP_CONFIG_JSON)
    jumbotron_info = {
        SITE_TITLE: config_dict.get(SITE_TITLE, ""),
        SITE_DESC: config_dict.get(SITE_DESC, ""),
    }
    return jumbotron_info


def add_form_to_addendum_dict(form: ImmutableMultiDict, addendum_dict: dict):
    """
    Used to update the addendum_dict that contains the previous graphic
     selection elements with a new set of selections from a posted form
    :param form:
    :param addendum_dict:
    :return:
    """
    graphic_dict = {}
    for key, value in form.lists():
        if key in [GRAPHIC_NAME, PROCESS]:
            continue
        graphic_dict[key] = value
    addendum_dict[form.get(GRAPHIC_NAME)] = graphic_dict
