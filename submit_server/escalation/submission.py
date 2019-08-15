# Submit a CS

import os
import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify)
from flask import current_app as app
from werkzeug.utils import secure_filename

from . import database as db
from .files import *
from .dashboard import update_ml, update_auto, update_science
from escalation import scheduler


def arr2html(arr):
    if type(arr) == str:
        return arr
    out = "<ul>\n"
    out += "\n".join("<li>%s</li>" % x for x in arr)
    out += "\n</ul>\n"
    return out


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['csv']


bp = Blueprint('submission', __name__)


def validate_submission_form(request_form, request_files):
    for key in ('username', 'expname', 'crank', 'notes', 'githash'):
        if key not in request_form:
            raise ValidationError("Key %s not present in POST" % key)

    username = request_form['username']
    expname = request_form['expname']
    crank = request_form['crank']
    notes = request_form['notes']
    githash = request_form['githash']
    csvfile = request_files['csvfile']

    app.logger.info("POST {} {} {} {} {}".format(username, expname, crank, notes, csvfile.filename))

    if not username:
        raise ValidationError('Username is required.')
    if not expname:
        raise ValidationError('Experiment name is required.')
    elif not crank:
        raise ValidationError('Crank number is required (e.g. 0015)')
    elif not githash or len(githash) != 7:
        raise ValidationError('7 char git hash is required (e.g. abc1234)')
    elif not csvfile or not allowed_file(csvfile.filename):
        raise ValidationError("Must upload a csv file")
    elif not db.is_stateset_active(crank, githash):
        raise ValidationError("Entered crank number %s is not active" % (crank))
    return username, expname, crank, notes, githash, csvfile


@bp.route('/submission', methods=('POST',))
def submission():
    if request.headers.get('User-Agent') != 'escalation':
        for key in ('username', 'expname', 'crank', 'notes', 'githash'):
            session[key] = request.form[key]

    try:
        # check the submission form
        username, expname, crank, notes, githash, csvfile = validate_submission_form(request.form, request.files)
        # if the form of the submission is right, let's validate the content of the submitted file
        rows, comments = text2rows(csvfile.read().decode('utf-8'))
        validate_submission(rows, crank, githash)
        if comments:
            notes = notes + "\nComments from file:" + comments
        db.add_submission(username, expname, crank, githash, rows, notes)
    except ValidationError as e:
        app.logger.info(e)
        # custom check if POST from script instead of UI
        if request.headers.get('User-Agent') == 'escalation':
            return jsonify({'error': e}), 400
        else:
            flash(arr2html(e))

    app.logger.info("Added submission")
    # kick off stats refresh
    job1 = scheduler.add_job(func=update_science, args=[], id='update_science')
    job2 = scheduler.add_job(func=update_auto, args=[], id='update_auto')
    job3 = scheduler.add_job(func=update_ml, args=[], id='update_ml')
    if request.headers.get('User-Agent') == 'escalation':
        return jsonify({'success': 'Added submission'})
    else:
        # clear out session
        for key in ('username', 'expname', 'crank', 'notes', 'githash'):
            session.pop(key, None)
        return render_template('success.html', username=username)


@bp.route('/submission', methods=('GET',))
def submission_view():
    curr_cranks = " ".join(sorted(x.crank for x in db.get_active_cranks()))
    return render_template('submission.html', session=session, curr_cranks=curr_cranks)
