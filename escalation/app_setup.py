# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0


import os
from types import MappingProxyType

from flask import Flask
from sqlalchemy.engine.url import URL

from app_deploy_data.app_settings import DATABASE_CONFIG
from controller import create_labels_for_available_pages, make_pages_dict
from utility.constants import (
    APP_CONFIG_JSON,
    AVAILABLE_PAGES,
    CONFIG_FILE_FOLDER,
    AVAILABLE_PAGES_DICT,
    DATA_BACKEND,
    POSTGRES,
)
from version import VERSION


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL")
        or URL(**DATABASE_CONFIG),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        VERSION=VERSION,
    )

    # register url blueprints with the app object
    from views.dashboard import dashboard_blueprint

    app.register_blueprint(dashboard_blueprint)
    from views.file_upload import upload_blueprint

    app.register_blueprint(upload_blueprint)
    from views.admin import admin_blueprint

    app.register_blueprint(admin_blueprint)

    @app.context_processor
    def get_dashboard_pages():
        # used for the navigation bar
        available_pages = app.config.get(APP_CONFIG_JSON)[AVAILABLE_PAGES]
        dashboard_pages = create_labels_for_available_pages(available_pages)
        return dict(dashboard_pages=dashboard_pages)

    return app


def configure_app(app, config_dict, config_file_folder):
    # write the config dict to app config as a read-only proxy of a mutable dict
    app.config[APP_CONFIG_JSON] = MappingProxyType(config_dict)
    config_file_folder = config_file_folder
    app.config[CONFIG_FILE_FOLDER] = config_file_folder
    app.config[AVAILABLE_PAGES_DICT] = make_pages_dict(
        config_dict[AVAILABLE_PAGES], app.config[CONFIG_FILE_FOLDER]
    )
    configure_backend(app)
    app.config.active_data_source_filters = {}
    return app


def configure_backend(app):
    # setup steps unique to SQL-backended apps
    if app.config[APP_CONFIG_JSON][DATA_BACKEND] in [POSTGRES]:
        from database.sql_handler import SqlHandler, SqlDataInventory
        from database.database import db, db_session

        db.init_app(app)
        data_backend_class = SqlHandler
        data_backend_writer = SqlDataInventory

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            db_session.remove()

    else:
        from database.local_handler import LocalCSVHandler, LocalCSVDataInventory

        data_backend_class = LocalCSVHandler
        data_backend_writer = LocalCSVDataInventory

    app.config.data_handler = data_backend_class
    app.config.data_backend_writer = data_backend_writer
