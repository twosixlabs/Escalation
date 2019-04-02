
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler

import atexit
import click
import logging
from logging.handlers import RotatingFileHandler
# create and configure the app

db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()
atexit.register(lambda: scheduler.shutdown())

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    
    app.config.from_mapping(
        SECRET_KEY='dev',
        #        DATABASE=os.path.join(app.instance_path, 'escalation.sqlite'),
        UPLOAD_FOLDER = os.path.join(app.instance_path,'submissions'),
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(app.instance_path,'escalation.sqlite'),
        #16 MB max upload
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024,
        ADMIN_KEY='secret',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    
    db.init_app(app)
    migrate.init_app(app,db)

    if not scheduler.running:
        scheduler.init_app(app)        
        scheduler.start()

        
    # ensure the instance folder exists
    try:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
    except OSError:
        pass

    from .submission import bp as sub_bp
    app.register_blueprint(sub_bp)
    
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

    @app.cli.command('update-ml')
    def update_ml_cli():
        from .dashboard import update_ml
        update_ml()

    @app.cli.command('job')
    def do_job():
        from .plot import update_runs_per_crank2
        update_runs_per_crank2()
        
    # Shut down the scheduler when exiting the app
    return app

