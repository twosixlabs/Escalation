import os
from flask import  Blueprint, flash, render_template, request, send_file, jsonify, redirect, url_for
from flask import current_app as app
from . import database as db
from .files import download_zip
from .policy import download_uniform_policy, default_models
from .dashboard import update_auto
from escalation import scheduler, PERSISTENT_STORAGE, UPLOAD_FOLDER

bp = Blueprint('submissions_overview', __name__)

DOWNLOAD_TRAINING_DATA = 'Download training data'


def init_view():
    cranks = db.get_unique_cranks()
    training_data_available_to_download = db.get_cranks_available_for_download()
    curr_crank = 'all'
    models = []
    policy_crank = None
    if cranks:
        policy_crank = cranks[0]
        print(policy_crank)
        models = db.get_submissions(policy_crank)
    if request.method == 'POST' and 'crank' in request.form:
        curr_crank = request.form['crank']
    submissions = db.get_submissions(curr_crank)
    return training_data_available_to_download, models, policy_crank, submissions, curr_crank, cranks


@bp.route('/submissions_overview', methods=('GET', 'POST'))
def submissions_overview():
    training_data_available_to_download, models, policy_crank, submissions, curr_crank, cranks = init_view()
    if request.form.get('policy_crank'):
        policy_crank = request.form['policy_crank']
        models = db.get_submissions(policy_crank)
    return render_template('submissions_overview.html',
                           submissions=submissions,
                           cranks=cranks,
                           curr_crank=curr_crank,
                           models=models,
                           policy_crank=policy_crank,
                           defaults=default_models,
                           training_data_available_to_download=training_data_available_to_download)


@bp.route('/submission_files/delete', methods=('POST',))
def delete_submission_files():
    if request.form['adminkey'] != app.config['ADMIN_KEY']:
        flash("Incorrect admin code")
    else:
        requested = [int(x) for x in request.form.getlist('download')]
        for id in requested:
            db.remove_submission(id)
    _ = scheduler.add_job(func=update_auto, args=[], id='update_auto')
    return redirect(url_for('submissions_overview.submissions_overview'))


@bp.route('/submission_files/download', methods=('POST',))
def download_submission_files():
    _, models, __, submissions, curr_crank, ___ = init_view()
    if request.form['submit'] == 'Download files':
        requested = [int(x) for x in request.form.getlist('download')]
        submissions = [sub for sub in submissions if sub.id in requested]
        app.logger.info(
            "Downloading %d submissions of %d requested for crank %s" % (len(submissions), len(requested), curr_crank))
        zipfile = download_zip(app.config[UPLOAD_FOLDER], submissions, curr_crank)
        return send_file(os.path.join(app.config[UPLOAD_FOLDER], zipfile), as_attachment=True)


@bp.route('/download_training', methods=('POST',))
def download_training():
    return send_file(os.path.join(app.config[PERSISTENT_STORAGE], request.form['download_training_crank']),
                     as_attachment=True)


def validate_policy_crank(size, requested):
    try:
        size = int(size)
    except ValueError:
        return "Passed in value '%s' for number of samples is not an integer"
    if size < 1:
        return "Number of samples must be greater than 0"
    elif len(requested) == 0:
        return "Must select a model to include"
    return


@bp.route('/policy/download', methods=('POST',))
def policy_crank_download():
    policy_crank = request.form['policy_crank']
    size = request.form['cranksize']
    submissions = db.get_submissions(policy_crank)
    requested = [int(x) for x in request.form.getlist('policy_download')]
    submissions = [sub for sub in submissions if sub.id in requested]
    err = validate_policy_crank(size, requested)
    if err:
        flash(err)
    else:
        zipfile, explanation = download_uniform_policy(app.config[UPLOAD_FOLDER], submissions, size, policy_crank)
        flash(explanation)
        app.logger.info(explanation)
        return send_file(os.path.join(app.config[UPLOAD_FOLDER], zipfile), as_attachment=True)
