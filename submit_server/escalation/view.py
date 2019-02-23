import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from escalation.db import get_db
from escalation.download import download_zip

bp = Blueprint('view', __name__)
@bp.route('/', methods=('GET','POST'))

def view():
    db = get_db()
    cranks = db.execute("SELECT DISTINCT crank FROM cranks ORDER by crank DESC").fetchall()
    cranks = [ x['crank'] for x in cranks]

    crank = "all"
    
    if request.method == 'POST' and 'crank' in request.form:
        crank = request.form['crank']
    
    if request.method == 'POST' and 'download' in request.form:
        print("files",request.form.getlist('download'))

        
    if request.method == 'POST' and crank != 'all':
        crank = request.form['crank']
        query = "SELECT id, username, expname, crank, filename, notes, created FROM submission WHERE crank = '%s' ORDER BY created DESC" % crank
    else:
        query = "SELECT id, username, expname, crank, filename, notes, created FROM submission ORDER BY created DESC"
        
    submissions = db.execute(query).fetchall()
            
    return render_template('index.html', submissions=submissions,cranks=cranks, crank=crank)
