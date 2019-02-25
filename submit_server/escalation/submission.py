# Submit a CS

import pandas as pd
import os
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from werkzeug.utils import secure_filename

from escalation.db import add_submission, get_current_crank
from escalation.validate import validate_submission


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['csv']



bp = Blueprint('submission', __name__)

@bp.route('/submission', methods=('GET', 'POST'))
def submission():
    if request.method == 'POST':

        for key in ('username','expname','crank','notes'):
            session[key] = request.form[key]

        username = request.form['username']
        expname  = request.form['expname']        
        crank    = request.form['crank']
        notes    = request.form['notes']        
        csvfile  = request.files['csvfile']
        curr_crank = get_current_crank()
        error = None
        if not username:
            error = 'Username is required.'
        if not expname:
            error = 'Experiment name is required.'            
        elif not crank:
            error = 'Crank number is required (e.g. 0015)'
        elif not csvfile or not allowed_file(csvfile.filename):
            error = "Must upload a csv file"
        elif crank != curr_crank:
            error = "Entered crank number (%s) does not match the current crank (%s)" % (crank, curr_crank)

        #save temporary local copy
        filename = secure_filename("_".join([crank,username,expname,csvfile.filename]))
        csvfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if not error:
            error = validate_submission(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if error:
            flash(error)
        else:
            add_submission(username,expname,crank,filename,notes)
            
            #clear out session
            for key in ('username','expname','crank','notes'):
                session.pop(key,None)
                
            return render_template('success.html',username=username)

    return render_template('submission.html',session=session)
