# Submit a CS

import os
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask import current_app as app
from werkzeug.utils import secure_filename

from .  import database as db
from .validate import validate_submission


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['csv']



bp = Blueprint('submission', __name__)

@bp.route('/submission', methods=('GET', 'POST'))
def submission():

    
    curr_crank = db.get_current_crank()

    if curr_crank is None:
        return render_template('submission.html')
    else:
        curr_crank = curr_crank.crank
        
    curr_stateset = db.get_stateset()[0]['stateset']
    
    if request.method == 'POST':
        for key in ('username','expname','crank','notes'):
            session[key] = request.form[key]

        username = request.form['username']
        expname  = request.form['expname']        
        crank    = request.form['crank']
        notes    = request.form['notes']        
        csvfile  = request.files['csvfile']

        app.logger.info("POST {} {} {} {} {}".format(username,expname,crank,notes,csvfile.filename))
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
            #TODO: pass in stateset/git hash here
            error = validate_submission(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        app.logger.info("Processed {}".format(csvfile.filename)            )
        #custom check if POST from script instead of UI
        if request.headers.get('User-Agent') == 'escalation':
            if error:
                app.logger.error(error)
                return jsonify({'error':error}), 400
            else:
                db.add_submission(username,expname,crank,filename,notes)
                app.logger.info("Added submission")                
                return jsonify({'success':'Added submission'})

        #case of web based user agent
        if error:
            app.logger.error(error)
            flash(error)
        else:
            db.add_submission(username,expname,crank,filename,notes)
            app.logger.info("Added submission")            

            #clear out session
            for key in ('username','expname','crank','notes'):
                session.pop(key,None)
                
            return render_template('success.html',username=username)

        
    return render_template('submission.html',session=session,crank=curr_crank,stateset=curr_stateset)
