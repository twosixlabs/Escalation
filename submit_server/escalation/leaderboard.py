from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_file
)
from flask import current_app as app
from . import database as db
import os
import csv
import time

def create_leaderboard_csv():
    rows = [x.__dict__ for x in db.get_leaderboard()]
    fieldnames = ['dataset_name','githash','run_id','created','model_name','model_author','accuracy','balanced_accuracy','auc_score','average_precision','f1_score','precision','recall','samples_in_train','samples_in_test','model_description','column_predicted','num_features_used','data_and_split_description','normalized','num_features_normalized','feature_extraction','was_untested_data_predicted']
    csvfile = os.path.join(app.config['UPLOAD_FOLDER'],"escalation.leaderboard.%s.csv" % time.strftime("%Y-%m-%d-%H%M%S",time.localtime()))
    with open(csvfile,'w') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames,lineterminator='\n',extrasaction='ignore')
        writer.writeheader()
        for elem in rows:
            writer.writerow(elem)
    return csvfile
    
bp = Blueprint('leaderboard', __name__)
@bp.route('/leaderboard', methods=('GET','POST'))
def leaderboard():
    if request.method == 'POST' and request.headers.get('User-Agent') == 'escalation':
        error = db.add_leaderboard(request.form)
        if error:
            app.logger.info(error)
            return jsonify({'error':error}), 400

    elif  request.method == 'POST' and request.form['submit'] == 'Download CSV':
        csvfile = create_leaderboard_csv()
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'],csvfile),as_attachment=True)            
            
    return render_template('leaderboard.html',table=db.get_leaderboard())

        
