DELIMITER = ','
BAD_DELIMITERS = set('\t, |.') - set(DELIMITER)  # common delimiters that are disallowed
import os
import pandas as pd
import hashlib

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask import current_app as app
from werkzeug.utils import secure_filename
from escalation.db import get_db, get_cranks, is_stateset_stored, set_stateset, get_stateset

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

    #TODO
    for r in get_stateset():
        print(r['dataset'],r['name'],r['_rxn_M_inorganic'],r['_rxn_M_organic'])
    error = None
    
    if request.method == 'GET':
        #clear POST variables between sessions
        for key in session_vars:
            session.pop(key,None)
                
    if request.method == 'POST':
        #save form values to pre-populate if there's an error so user saves time
        for key in session_vars:
            session[key] = request.form[key]

        csvfile  = request.files['csvfile']
        username = request.form['username']
        crank = request.form['crank']                
        filename = secure_filename(csvfile.filename)
        outfile  = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        githash  = request.form['githash']

        csvfile.save(outfile)
        error = validate(request.form['adminkey'],githash,outfile)

        if error == None:
            stateset = md5(outfile)[:11]
            #check if stateset hash was already stored
            #TODOerror = is_stateset_stored(stateset)
                
        if error:
            print("Error",error)
            flash(error)
        else:
            num_rows = set_stateset(crank,stateset,outfile,githash,username)
            
            flash("Successfully updated to crank %s and stateset %s with %d rows" % (crank, stateset,num_rows))
            for key in session_vars:
                session.pop(key,None)
                
        #custom check if POST from script instead of UI
        if request.headers.get('User-Agent') == 'escalation':
            if error:
                return jsonify({'error':error}), 400
            else:
                return jsonify({'success':'Added updated to crank %s and stateset hash %s with %d rows' % (crank,stateset,num_rows)}), 200

    cranks = get_cranks()
    return render_template('admin.html',cranks=cranks,session=session)
