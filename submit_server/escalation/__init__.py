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

app = Flask(__name__, instance_relative_config=True)

app.config.from_mapping(
    SECRET_KEY='dev',
    #        DATABASE=os.path.join(app.instance_path, 'escalation.sqlite'),
    UPLOAD_FOLDER = os.path.join(app.instance_path,'submissions'),
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(app.instance_path,'escalation.sqlite'),
    #32 MB max upload
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024,
    ADMIN_KEY='secret',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
scheduler = APScheduler()
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

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

@app.route('/links')
def links():
    return render_template('links.html')

from . import submission
from . import view
from . import admin
from . import dashboard

app.register_blueprint(submission.bp)
app.register_blueprint(view.bp)
app.register_blueprint(admin.bp)            
app.register_blueprint(dashboard.bp)

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


#@app.shell_context_processor
#def make_shell_context():
#    return {'db': db, 'Run':database}

from .database import insert_demo_data, delete_db, create_db, Run, Submission, Crank, Prediction

@app.cli.command('reset-db')
def reset_db():
    delete_db()
    click.echo("Deleted db entries")

@app.cli.command('demo-db')
def demo_data():
    insert_demo_data()
    click.echo("Added demo data")    


# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
