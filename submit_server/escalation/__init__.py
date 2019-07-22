
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler

import atexit
import click
import logging
from logging.handlers import RotatingFileHandler

from .constants import PERSISTENT_STORAGE, TRAINING_DATA_PATH, STATESETS_PATH


# create and configure the app

db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()
atexit.register(lambda: scheduler.shutdown())


def build_persistent_storage_dirs(app):
    # ensure the instance folder exists
    for path_ in (
            app.config[PERSISTENT_STORAGE],
            app.instance_path,
            os.path.join(app.config[PERSISTENT_STORAGE], STATESETS_PATH),
            os.path.join(app.config[PERSISTENT_STORAGE], TRAINING_DATA_PATH)
    ):
        if not os.path.exists(path_):
            os.makedirs(path_)


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        # PERSISTENT_STORAGE=os.environ.get('ESCALATION_PERSISTENT_DATA_PATH', '../escalation_data'),
        # add local development persistent storage option
        PERSISTENT_STORAGE=os.environ.get('ESCALATION_PERSISTENT_DATA_PATH'),
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(app.instance_path,'escalation.sqlite'),
        #1GB max upload
        MAX_CONTENT_LENGTH = 1024 * 1024 * 1024,
        ADMIN_KEY='Trompdoy',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)
    migrate.init_app(app,db)

    if not scheduler.running:
        scheduler.init_app(app)        
        scheduler.start()

    build_persistent_storage_dirs(app)

    from .submission import bp as sub_bp
    app.register_blueprint(sub_bp)

    from .feature_analysis import bp as feat_bp
    app.register_blueprint(feat_bp)
    
    from .view import bp as view_bp
    app.register_blueprint(view_bp)
    
    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from . import dashboard    
    app.register_blueprint(dashboard.bp)

    from . import leaderboard
    app.register_blueprint(leaderboard.bp)

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/escalation.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('ESCALATion started')    

        app.logger.info("Writing to %s" % app.config['SQLALCHEMY_DATABASE_URI'])

    from .database import delete_db, create_db, Run, Submission, Crank, Prediction

    @app.cli.command('reset-db')
    def reset_db():
        delete_db()
        click.echo("Deleted db entries")

    @app.cli.command('init-db')
    def init_db():
        create_db()
        click.echo("Created db")

    @app.cli.command('update-ml')
    def update_ml_cli():
        from .dashboard import update_ml
        update_ml()

    @app.cli.command('job')
    def do_job():
        from .plot import update_repo_table
        update_repo_table()
        
    # Shut down the scheduler when exiting the app
    return app

