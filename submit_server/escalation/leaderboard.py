from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask import current_app as app
from . import database as db


bp = Blueprint('leaderboard', __name__)
@bp.route('/leaderboard', methods=('GET','POST'))
def leaderboard():
    if request.method == 'POST':
        error = db.add_leaderboard(request.form)

        if error:
            app.logger.info(error)
            return jsonify({'error':error}), 400
        
    return render_template('leaderboard.html',table=db.get_leaderboard())

        
