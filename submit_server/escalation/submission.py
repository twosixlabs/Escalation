# Submit a CS

import os
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask import current_app as app
from werkzeug.utils import secure_filename

from .  import database as db
from .files import *

def arr2html(arr):
    if type(arr) == str:
        return arr
    out="<ul>\n"
    out += "\n".join("<li>%s</li>" % x for x in arr)
    out += "\n</ul>\n"
    return out


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['csv']



bp = Blueprint('submission', __name__)

@bp.route('/submission', methods=('GET', 'POST'))
def submission():

    curr_crank = db.get_current_crank()
    if curr_crank is None:
        print("HERE")
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
        else:
            
            rows, comments = text2rows(csvfile.read().decode('utf-8'))
            if rows == None:
                error = "Could not extract rows from file %s" % csvfile.filename
            if error == None:
                error = validate_submission(rows,curr_stateset)
            if error == None:
                if comments:
                    notes = notes + "\nComments from file:" + comments
                error = db.add_submission(username,expname,crank,rows,notes)

        #custom check if POST from script instead of UI
        if error:
            #turn into array for downstream printing -- bleh I know
            if type(error) == str:
                error = [error]
            app.logger.info("\n".join(error))
            if request.headers.get('User-Agent') == 'escalation':
                return jsonify({'error':error}), 400
            else:
                flash(arr2html(error))
        else:
            app.logger.info("Added submission")
            if request.headers.get('User-Agent') == 'escalation':                
                return jsonify({'success':'Added submission'})
            else:
                #clear out session
                for key in ('username','expname','crank','notes'):
                    session.pop(key,None)
                
                return render_template('success.html',username=username)

    return render_template('submission.html',session=session,crank=curr_crank,stateset=curr_stateset)
