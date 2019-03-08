DELIMITER = ','
BAD_DELIMITERS = set('\t, |.') - set(DELIMITER)  # common delimiters that are disallowed
import os
import csv
import hashlib

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask import current_app as app
from werkzeug.utils import secure_filename
from . import database as db

session_vars= ('githash','adminkey','username','crank')
# check that admin key is correct, git commit is 7 digits and csv file is the right format
def validate(adminkey,githash,filename):
    if adminkey != app.config['ADMIN_KEY']:
        return "Wrong admin key"
    
    if len(githash) != 7:
        return "Git commit hash is not 7 characters (current length is %d)" % len(githash)

    #make sure file is comma  delimited
    with open(filename, 'r') as fh:
        for header in fh:
            if header[0] != '#':
                break

    required_header="dataset,name,_rxn_M_inorganic,_rxn_M_organic"
    if header.strip() != required_header:
        return "csv file does not have required header '%s'" % required_header
    
    return None

bp = Blueprint('admin',__name__)
@bp.route('/admin', methods=('GET','POST'))
def admin():

    error = None
    
    if request.method == 'GET':
        #clear POST variables between sessions
        for key in session_vars:
            session.pop(key,None)
                
    if request.method == 'POST' and 'username' in request.form:
        #save form values to pre-populate if there's an error so user saves time
        for key in session_vars:
            session[key] = request.form[key]

        csvfile  = request.files['csvfile']
        username = request.form['username']
        crank = request.form['crank']                
        filename = secure_filename(csvfile.filename)
        outfile  = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        githash  = request.form['githash']

        app.logger.info("request: {} {} {} {}".format(csvfile.filename,username,crank,githash))

        csvfile.save(outfile)
        error = validate(request.form['adminkey'],githash,outfile)
        app.logger.info("Validated %s" % csvfile.filename)
        
        if error == None:
            #get statset from first element
            with open(outfile) as csv_file:
                csv_reader = csv.DictReader(filter(lambda row: row[0]!='#', csv_file))
                for row in csv_reader:
                    stateset = row['dataset']
                    break
                
            #check if stateset hash was already stored
            error = db.is_stateset_stored(stateset)
                
        if error:
            app.logger.error(error)
            flash(error)
        else:
            num_rows = db.add_stateset(crank,stateset,outfile,githash,username)
            out="Successfully updated to crank %s and stateset %s with %d rows" % (crank, stateset,num_rows)
            app.logger.info(out)
            flash(out)
            for key in session_vars:
                session.pop(key,None)

        #custom check if POST from script instead of UI
        if request.headers.get('User-Agent') == 'escalation':
            if error:
                return jsonify({'error':error}), 400
            else:
                return jsonify({'success':'updated to crank %s and stateset hash %s with %d rows' % (crank,stateset,num_rows)}), 200

    if request.method == 'POST' and 'new_stateset' in request.form:
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:
            res = db.get_stateset(request.form['new_stateset'])
            if res is None:
                flash("Something went wrong getting stateset id",request.form['new_stateset'])
            else:
                flash("Updating stateset to crank %s and hash %s" % (res['crank'], res['stateset']))
                db.set_stateset(res['id'])
                app.logger.info("Updating stateset to crank %s and hash %s" % (res['crank'], res['stateset']))
                
    cranks = db.get_cranks()
    print(cranks)
    return render_template('admin.html',cranks=cranks,session=session)
