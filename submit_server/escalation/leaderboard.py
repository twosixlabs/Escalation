import csv
import os
import time

from flask import Blueprint, render_template, request, jsonify, send_file
from flask import current_app as app

from escalation import database, scheduler
from escalation.dashboard import update_ml


def create_leaderboard_csv():
    rows = [x.__dict__ for x in database.get_leaderboard()]
    fieldnames = ['dataset_name', 'githash', 'run_id', 'created', 'model_name', 'model_author', 'accuracy',
                  'balanced_accuracy', 'auc_score', 'average_precision', 'f1_score', 'precision', 'recall',
                  'samples_in_train', 'samples_in_test', 'model_description', 'column_predicted', 'num_features_used',
                  'data_and_split_description', 'normalized', 'num_features_normalized', 'feature_extraction',
                  'was_untested_data_predicted']
    csvfile = os.path.join(app.config['UPLOAD_FOLDER'],
                           "escalation.leaderboard.%s.csv" % time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))
    with open(csvfile, 'w') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        for elem in rows:
            writer.writerow(elem)
    return csvfile


bp = Blueprint('leaderboard', __name__)


@bp.route('/leaderboard', methods=('GET', 'POST'))
def leaderboard():
    if request.method == 'POST' and request.headers.get('User-Agent') == 'escalation':
        error = database.add_leaderboard(request.form)
        if error:
            app.logger.info(error)
            return jsonify({'error': error}), 400

        job3 = scheduler.add_job(func=update_ml, args=[], id='update_ml')
    elif request.method == 'POST' and request.form['submit'] == 'Download CSV':
        csvfile = create_leaderboard_csv()
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], csvfile), as_attachment=True)
    elif request.method == 'POST' and 'submit' in request.form and request.form['submit'] == 'Delete':
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            # flash("Incorrect admin code")
            return J
        else:
            requested = [int(x) for x in request.form.getlist('delete')]
            for id in requested:
                database.remove_leaderboard(id)

            job3 = scheduler.add_job(func=update_ml, args=[], id='update_ml')

    return render_template('leaderboard.html', table=database.get_all_leaderboard_entries())
