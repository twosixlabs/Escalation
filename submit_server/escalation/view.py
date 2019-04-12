from collections import OrderedDict
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file
)
from flask import current_app as app
from . import database as db
from .files import download_zip
from .dashboard import update_auto, update_science
from escalation import scheduler

bp = Blueprint('view', __name__)
@bp.route('/', methods=('GET','POST'))

def view():
    curr_crank = "all"
    
    if request.method == 'POST' and 'crank' in request.form:
        curr_crank = request.form['crank']

    if request.method == 'POST' and 'submit' in request.form and request.form['submit'] == 'Delete file':
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:
            requested=[int(x) for x in request.form.getlist('download')]
            for id in requested:
                db.remove_submission(id)
        job2 = scheduler.add_job(func=update_auto, args=[], id = 'update_auto')        

    submissions=db.get_submissions(curr_crank)

    if request.method == 'POST' and  'submit' in request.form and request.form['submit'] == 'Download files':
        requested=[int(x) for x in request.form.getlist('download')]
        submissions = [sub for sub in submissions if sub.id in requested]
        zipfile = download_zip(app.config['UPLOAD_FOLDER'],submissions, curr_crank)
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'],zipfile),as_attachment=True)
    
    return render_template('index.html',submissions=submissions,cranks=db.get_unique_cranks(), crank=curr_crank)
