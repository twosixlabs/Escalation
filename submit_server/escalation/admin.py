DELIMITER = ','
BAD_DELIMITERS = set('\t, |.') - set(DELIMITER)  # common delimiters that are disallowed
import os
import csv
import hashlib

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.utils import secure_filename
from flask import current_app as app
from . import database as db

session_vars= ('githash','adminkey','username','crank')
# check that admin key is correct, git commit is 7 digits and csv file is the right format
def validate(adminkey,githash,filename):
    if adminkey != app.config['ADMIN_KEY']:
        return "Wrong admin key"
    
    if len(githash) != 7:
        return "Git commit hash is not 7 characters (current length is %d)" % len(githash)

    header=""
    #make sure file is comma  delimited
    with open(filename, 'r') as fh:
        for header in fh:
            print(header)
            if header[0] != '#':
                break

    required_header="dataset,name,_rxn_M_inorganic,_rxn_M_organic,_rxn_M_acid"
    if header.strip() != required_header:
        return "csv file does not have required header '%s'" % required_header
    
    return None

bp = Blueprint('admin',__name__)
@bp.route('/admin', methods=('GET','POST'))
def admin():
    error = None
                
    if request.method == 'POST' and request.headers.get('User-Agent') == 'escalation':
        stateset  = request.files['stateset']
        stateset_file  = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(stateset.filename))

        training = request.files['perovskitedata']
        training_file = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(training.filename))
                
        username = request.form['username']
        crank = request.form['crank']                
        githash  = request.form['githash']

        app.logger.info("Received request: {} {} {} {} {}".format(stateset_file,training_file,username,crank,githash))

        if db.is_stateset_stored(crank,githash):
            error = 'Crank and githash already stored in database'
        else:
            stateset.save(stateset_file)
            training.save(training_file)
            error = validate(request.form['adminkey'],githash,stateset_file)

        if error == None:
            num_rows       = db.add_stateset(stateset_file,crank,githash,username)
            num_train_rows = db.add_training(training_file)

            out="Successfully updated to crank %s and stateset %s with %d rows" % (crank, githash,num_rows)
            app.logger.info(out)
            return jsonify({'success':'updated to crank %s and commit hash %s with %d rows' % (crank,githash,num_rows)}), 200        
        else:
            app.logger.error(error)            
            return jsonify({'error':error}), 400

    if request.method == 'POST' and request.form['submit'] == "Update active cranks":
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:

            # check that only one crank has been set to active
            seen={}
            cranks = db.get_cranks()
            for crank in cranks:
                id = str(crank.id)
                if id in request.form and request.form[id] == 'active':
                    if crank.crank in seen:
                        flash("Can only have one active row for crank %s" % crank.crank)
                        cranks=[] #cute way to prevent updating any cranks below
                        break
                    seen[crank.crank] = 1

            # now update cranks
            for crank in cranks:
                id = str(crank.id)
                if id not in request.form:
                    continue

                new_status = request.form[id] == 'active'
                if new_status != crank.active:
                    db.update_crank_status(crank.id,new_status)
                    out="Updating crank %s to %s" % (crank.crank,  'active' if new_status else 'inactive')
                    flash(out)
                    app.logger.info(out)
                    
    if request.method == 'POST' and  request.form['submit'] == 'Update Database' :
        for k in request.form:
            app.logger.info(k)
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:
            from .database import delete_db
            if request.form['db'] == 'reset':
                delete_db()
                app.logger.info("Deleted all data")
                flash("Deleted all data")
            else:
                flash("Unknown command, doing nothing")
            
            
    cranks = db.get_cranks()
    return render_template('admin.html',cranks=cranks,session=session)
