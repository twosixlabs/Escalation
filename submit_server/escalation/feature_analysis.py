from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_file
)
from flask import current_app as app
from . import database as db
import os
import csv

from .dashboard import update_science
from escalation import scheduler

bp = Blueprint('feature_analysis', __name__)
@bp.route('/features', methods=('GET','POST'))
def feature_analysis():
    if request.method == 'POST' and request.headers.get('User-Agent') == 'escalation':
        error = db.add_feature_analysis(request.json)
        if error:
            app.logger.info(error)
            return jsonify({'error':error}), 400

        job3 = scheduler.add_job(func=update_science, args=[], id = 'update_science')                    
    elif request.method == 'POST' and 'submit' in request.form and request.form['submit'] == 'Delete':
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:
            requested=[int(x) for x in request.form.getlist('delete')]
            for id in requested:
                db.remove_feature_analysis(id)

            job3 = scheduler.add_job(func=update_science, args=[], id = 'update_science')                    
            
    return render_template('feature_analysis.html',table=[x.__dict__ for x in db.get_feature_analysis()])

        
