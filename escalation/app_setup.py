# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import importlib
import os
from types import MappingProxyType

from flask import Flask
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy

from controller import create_labels_for_available_pages, make_pages_dict
from utility.constants import (
    APP_CONFIG_JSON,
    AVAILABLE_PAGES,
    CONFIG_FILE_FOLDER,
    AVAILABLE_PAGES_DICT,
    DATA_BACKEND,
    POSTGRES,
    SQLALCHEMY_DATABASE_URI,
    DEVELOPMENT,
)
from app_deploy_data.app_settings import DATABASE_CONFIG
from version import VERSION
from views.dashboard import dashboard_blueprint
from views.file_upload import upload_blueprint
from views.admin import admin_blueprint
from views.download import download_blueprint
from views.wizard_view import wizard_blueprint


def create_app(db_uri=None):
    app = Flask(__name__)
    # specify the env variable DATABASE_CONFIG to control the content of DATABASE_CONFIG
    if db_uri:
        if isinstance(db_uri, URL):
            sqlalchemy_database_uri = db_uri
        elif isinstance(db_uri, str):
            sqlalchemy_database_uri = URL(db_uri)
        else:
            raise TypeError("db_uri must be url string or sqlalchemy URL object")
    else:
        sqlalchemy_database_uri = URL(**DATABASE_CONFIG)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=sqlalchemy_database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        VERSION=VERSION,
    )

    # register url blueprints with the app object
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(upload_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(download_blueprint)
    if app.config.get("ENV") == DEVELOPMENT:
        # only include the wizard blueprint when running in debug mode
        app.register_blueprint(wizard_blueprint)

    @app.context_processor
    def get_dashboard_pages():
        # used for the navigation bar
        available_pages = app.config.get(APP_CONFIG_JSON).get(AVAILABLE_PAGES, [])
        dashboard_pages = create_labels_for_available_pages(available_pages)
        return dict(dashboard_pages=dashboard_pages)

    return app


def configure_app(app, config_dict, config_file_folder):
    # write the config dict to app config as a read-only proxy of a mutable dict
    app.config[APP_CONFIG_JSON] = MappingProxyType(config_dict)
    config_file_folder = config_file_folder
    app.config[CONFIG_FILE_FOLDER] = config_file_folder
    app.config[AVAILABLE_PAGES_DICT] = make_pages_dict(
        config_dict.get(AVAILABLE_PAGES, []), app.config[CONFIG_FILE_FOLDER]
    )
    configure_backend(app)
    return app


def configure_backend(app, models_path="app_deploy_data.models"):
    # setup steps unique to SQL-backended apps
    if app.config[APP_CONFIG_JSON].get(DATA_BACKEND) in [POSTGRES]:
        from database.sql_handler import SqlHandler, SqlDataInventory

        app.db = SQLAlchemy()
        engine = create_engine(
            app.config[SQLALCHEMY_DATABASE_URI], convert_unicode=True
        )
        app.db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine)
        )
        app.db.init_app(app)

        data_backend_class = SqlHandler
        data_backend_writer = SqlDataInventory
        models_imports = importlib.import_module(models_path)
        app.Base = getattr(models_imports, "Base")

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            app.db_session.remove()

    else:
        from database.local_handler import LocalCSVHandler, LocalCSVDataInventory

        data_backend_class = LocalCSVHandler
        data_backend_writer = LocalCSVDataInventory

    app.config.data_handler = data_backend_class
    app.config.data_backend_writer = data_backend_writer
