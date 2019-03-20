from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask import current_app 
from . import database as db
from apscheduler.schedulers.background import BackgroundScheduler
import time

def background_task(task_id):
    for i in range(10):
        print("Running {} of {}".format(i,task_id))
        time.sleep(2)

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
def dashboard():
    ml=None
    auto=None
    science=None
    return render_template('dashboard.html',science=science,auto=auto,ml=ml)

@bp.route('/run-tasks')
def run_tasks():
    for i in range(10):
        current_app.apscheduler.add_job(func=background_task, trigger='date', args=[i], id = 'j' + str(i))
    return 'Scheduled several long running tasks.', 200
