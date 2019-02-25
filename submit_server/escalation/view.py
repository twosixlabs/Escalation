import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file
)
from flask import current_app as app
from escalation.db import get_db
from escalation.download import download_zip

bp = Blueprint('view', __name__)
@bp.route('/', methods=('GET','POST'))

def view():
    db = get_db()
    cranks = db.execute("SELECT DISTINCT Crank FROM Cranks ORDER by Crank DESC").fetchall()
    cranks = [ x['crank'] for x in cranks]

    if 'username' in g:
        print("Here")
        flash(g.username)
        
    curr_crank = "all"
    if request.method == 'POST' and 'crank' in request.form:
        curr_crank = request.form['crank']

    if curr_crank != 'all':
        query = "SELECT id, Username, Expname, Crank, Filename, Notes, Created FROM Submission WHERE Crank = '%s' ORDER BY Created DESC" % curr_crank
    else:
        query = "SELECT id, username, Expname, Crank, Filename, Notes, Created FROM Submission ORDER BY Created DESC"

    submissions = db.execute(query).fetchall()
        
    if request.method == 'POST' and 'download' in request.form:
        files=request.form.getlist('download')
        metadata = [dict(sub) for sub in submissions if sub['filename'] in files]
        zipfile = download_zip(app.config['UPLOAD_FOLDER'],files, curr_crank,metadata)
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'],zipfile),as_attachment=True)
    
    return render_template('index.html', submissions=submissions,cranks=cranks, crank=curr_crank)
