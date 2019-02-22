import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from escalation.db import get_db
bp = Blueprint('submission', __name__, url_prefix='/submission')

@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':
        username = request.form['username']
        crank = request.form['crank']
        notes = request.form['notes']        
#TODO        filename = request.form['filename']
        db = get_db()

        error = None
        if not username:
            error = 'Username is required.'
        elif len(username) < 5:
            error = "Username must be 5 chars or greater"
        elif not crank:
            error = 'Crank number is required (e.g. 0015)'

        #TODO: validate file
        if error is None:
            db.execute(
                'INSERT INTO submission (username, crank, notes) VALUES (?, ?, ?)',
                (username, crank, notes)
            )
            db.commit()
            return render_template('success.html')

        flash(error)

    return render_template('upload.html')
