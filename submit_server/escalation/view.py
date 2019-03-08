import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file
)
from flask import current_app as app
from . import database as db
from .download import download_zip

bp = Blueprint('view', __name__)
@bp.route('/', methods=('GET','POST'))

def view():
    cranks = db.get_unique_cranks()
        
    curr_crank = "all"
    if request.method == 'POST' and 'crank' in request.form:
        curr_crank = request.form['crank']

    submissions = db.get_submissions(curr_crank)
        
    if request.method == 'POST' and 'download' in request.form:
        files=request.form.getlist('download')
        metadata = [dict(sub) for sub in submissions if sub['filename'] in files]
        zipfile = download_zip(app.config['UPLOAD_FOLDER'],files, curr_crank,metadata)
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'],zipfile),as_attachment=True)
    
    return render_template('index.html', submissions=submissions,cranks=cranks, crank=curr_crank)
