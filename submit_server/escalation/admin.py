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
from escalation.db import get_db

session_vars= ('githash','adminkey','username')
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
        return "csv file does not have required header '%s' % required_header"
    
    return None

# fetch crank number, md5sum from file (md5sum is copy/pasted from versioned https://gitlab.sd2e.org/sd2program/versioned-datasets/blob/master/scripts/file_hash.py
def get_metadata(csvfile):
    md5sum = md5(csvfile)
    df = pd.read_csv(csvfile,comment='#')
    crank = "%04d" % df['dataset'][0]
    del df
    return crank, md5sum[:11]

bp = Blueprint('admin',__name__)
@bp.route('/admin', methods=('GET','POST'))
def admin():
    db = get_db()
    error = None
    
    if request.method == 'GET':
        for key in session_vars:
            session.pop(key,None)
                
    if request.method == 'POST':
        print(request.form)
        print(request.files['csvfile'].filename)
        #save form values to pre-populate if there's an error so user saves time
        for key in session_vars:
            session[key] = request.form[key]

        csvfile = request.files['csvfile']
        username = request.form['username']        
        filename = secure_filename(csvfile.filename)
        outfile = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        githash = request.form['githash']            
        csvfile.save(outfile)

        error = validate(request.form['adminkey'],githash,outfile)

        if error == None:
            crank, stateset = get_metadata(outfile)
            #check if row already in table
            res=db.execute('SELECT Created FROM Cranks WHERE Stateset=? AND Githash=?',
                           (stateset, githash)
            ).fetchall()
        
            if len(res) > 0:
                error = "State hash %s and git commit %s already in db. Created on %s" % (stateset,githash, ",".join(r['created'].strftime("%Y-%m-%d") for r in res))
        
        if error == None:
            #expire all other current cranks since we're updating to this one
            db.execute('UPDATE Cranks SET Current = "FALSE" WHERE Current = "TRUE"')
            
            #insert new entry
            db.execute(
                'INSERT INTO Cranks (Crank,Stateset,Filename,Githash,Username,Current)'
                'VALUES (?,?,?,?,?,?)',
                (crank,
                 stateset,
                 filename, #not outfile since thats absolute path
                 githash,
                 username,
                 "TRUE") #true is current
            )

            db.execute('DELETE FROM Stateset')
            
            db.commit()
            
            
            
            for key in session_vars:
                session.pop(key,None)
                
            flash("Successfully added crank info")

        #custom check if POST from script instead of UI
        if request.headers.get('User-Agent') == 'escalation':
            if error:
                return jsonify({'error':error}), 400
            else:
                return jsonify({'success':'Added crank %s with stateset hash %s' % (crank,stateset)}), 200

        if error:
            print("Error",error)
            flash(error)

    cranks = db.execute("SELECT * FROM Cranks ORDER by Created DESC").fetchall()
    return render_template('admin.html',cranks=cranks,session=session)
