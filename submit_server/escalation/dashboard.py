from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask import current_app 
from . import database as db
from apscheduler.schedulers.background import BackgroundScheduler
import time

bp = Blueprint('dashboard', __name__)


def update_science():
    current_app.logger.info("Updating science stats")    
    print("Updating science stats")

def update_auto():
    current_app.logger.info("Updating automation stats")

def update_ml():
    current_app.logger.info("Updating ML stats")
    
@bp.route('/dashboard', methods=('GET','POST'))
def dashboard():
    ml=None
    auto=None
    science=None


    if request.method == 'POST':
        if 'update_science' in request.form:
            flash("Refreshing Science stats...")
            current_app.apscheduler.add_job(func=update_science, trigger='date', args=[], id = 'update_science')
        elif 'update_auto' in request.form:
            flash("Refreshing Automation stats...")
            current_app.apscheduler.add_job(func=update_auto, trigger='date', args=[], id = 'update_auto')            
        elif 'update_ml' in request.form:
            flash("Refreshing ML stats...")            
            current_app.apscheduler.add_job(func=update_ml, trigger='date', args=[], id = 'update_ml')            
        else:
            flash("Unknown button!")
            
    return render_template('dashboard.html',science=science,auto=auto,ml=ml)

@bp.route('/run-tasks')
def run_tasks():
    for i in range(10):
        current_app.apscheduler.add_job(func=background_task, trigger='date', args=[i], id = 'j' + str(i))
    return 'Scheduled several long running tasks.', 200


