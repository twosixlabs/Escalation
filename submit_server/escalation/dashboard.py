from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask import current_app
from flask_table import Table, Col
from . import database as db
from apscheduler.schedulers.background import BackgroundScheduler
import time

bp = Blueprint('dashboard', __name__)

class StatsTable(Table):
    name = Col('Summary')
    value = Col('Description')
    date = None

class Stat(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

with app.app_context():        
    g.science_table = StatsTable([Stat(name='Blank mean',value=0.0),Stat(name='std',value=0.2)])
    g.ml_table = StatsTable([Stat(name='Blank mean',value=0.0),Stat(name='std',value=0.0)])
    g.auto_table = StatsTable([Stat(name='Blank mean',value=0.0),Stat(name='std',value=0.0)])

def update_science():
    current_app.logger.info("Updating science stats")
    sleep(5)    
    g.science_table = StatsTable([Stat(name='Science mean',value=0.2),Stat(name='std',value=0.2)])

def update_auto():
    current_app.logger.info("Updating automation stats")
    sleep(5)
    g.auto_table = StatsTable([Stat(name='auto mean',value=0.2),Stat(name='std',value=0.2)])    

def update_ml():
    current_app.logger.info("Updating ML stats")
    sleep(2)    
    g.ml_table = StatsTable([Stat(name='ml mean',value=0.2),Stat(name='std',value=0.2)])    
    
@bp.route('/dashboard', methods=('GET','POST'))
def dashboard():


    if request.method == 'POST':
        if 'update_science' in request.form:
            flash("Refreshing Science stats...")
            job = current_app.apscheduler.add_job(func=update_science, args=[], id = 'update_science')
        elif 'update_auto' in request.form:
            flash("Refreshing Automation stats...")
            job =current_app.apscheduler.add_job(func=update_auto, args=[], id = 'update_auto')            
        elif 'update_ml' in request.form:
            flash("Refreshing ML stats...")            
            job = current_app.apscheduler.add_job(func=update_ml, args=[], id = 'update_ml')            
        else:
            flash("Unknown button!")

        flash("Kicked off job {}".format(job))
            
    return render_template('dashboard.html',science_table=science_table,auto_table=auto_table,ml_table=ml_table)

