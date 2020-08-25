# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import os

from flask import Flask
from sqlalchemy.engine.url import URL

from utility.constants import (
    CONFIG_FILE_FOLDER,
    TEST_APP_DEPLOY_DATA,
    APP_DEPLOY_DATA,
    DATA_BACKEND,
)
from app_deploy_data.app_settings import DATABASE_CONFIG
from wizard_ui.wizard_utils import (
    load_main_config_dict_if_exists,
    set_up_backend_for_wizard,
)


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL")
        or URL(**DATABASE_CONFIG),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        VERSION="0.0.1",
    )

    # register url blueprints with the app object
    from wizard_ui.wizard_view import wizard_blueprint

    app.register_blueprint(wizard_blueprint)

    return app


def configure_app(app):
    app.config[CONFIG_FILE_FOLDER] = APP_DEPLOY_DATA
    config_dict = load_main_config_dict_if_exists(app)
    if config_dict and config_dict.get(DATA_BACKEND):
        set_up_backend_for_wizard(config_dict, app)
    return app


app = create_app()
app = configure_app(app)

if __name__ == "__main__":
    app.run()
