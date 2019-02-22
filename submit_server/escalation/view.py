import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from escalation.db import get_db


bp = Blueprint('view', __name__)
@bp.route('/')
def view():
    db = get_db()
    submissions = db.execute(
        'SELECT id, username, crank, filename, notes, created '
        ' FROM submission '
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('index.html', submissions=submissions)
