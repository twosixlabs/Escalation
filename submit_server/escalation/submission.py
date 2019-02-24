# Submit a CS

import pandas as pd
import os
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from werkzeug.utils import secure_filename

from escalation.db import get_db
from escalation.validate import validate_submission


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['csv']



bp = Blueprint('submission', __name__)

@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':
        username = request.form['username']
        expname = request.form['expname']        
        crank = request.form['crank']
        notes = request.form['notes']        
        csvfile = request.files['csvfile']
        db = get_db()

        error = None
        if not username:
            error = 'Username is required.'
        if not expname:
            error = 'Experiment name is required.'            
        elif not crank:
            error = 'Crank number is required (e.g. 0015)'
        elif not csvfile or not allowed_file(csvfile.filename):
            error = "Must upload a csv file"

        #save temporary local copy
        filename = secure_filename(csvfile.filename)
        csvfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        error = validate_submission(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if error is None:
            db.execute(
                'INSERT INTO Submission (Username, Expname,Crank, Filename,Notes) VALUES (?,?, ?, ?, ?)',
                (username,
                 expname,
                 crank,
                 filename,
                 notes)
            )
            db.commit()
            
            return render_template('success.html',username=username)
        
        flash(error)

    return render_template('upload.html')
