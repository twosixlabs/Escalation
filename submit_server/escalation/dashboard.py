from flask import (
    Blueprint, flash, g, redirect, render_template, request
)
from flask import current_app
from escalation import scheduler, db
from . import database
from .database import *
from collections import defaultdict
from sqlalchemy.sql import func

import time
import random
import heapq

TOP_PREDICTION_LIMIT=10

bp = Blueprint('dashboard', __name__)

def update_auto():
    app = scheduler.app
    app.logger.info("Updating automation stats")
    with app.app_context():
        cranks = database.get_cranks()
        AutomationStat.query.delete()
        seen = {}
        for crank in cranks:
            if crank.crank in seen:
                continue
            seen[crank.crank] = 1

            num_uploads = Submission.query.filter_by(crank=crank.crank).count()
            num_distinct_entries = db.session.query(Prediction.dataset,Prediction.name).filter_by(dataset=crank.crank).group_by(Prediction.dataset, Prediction.name).count()

            db.session.add(AutomationStat(crank=crank.crank,
                                          upload_date=crank.created,
                                          num_runs=crank.num_runs,
                                          num_uploads=num_uploads,
                                          num_distinct=num_distinct_entries
            )
            )
        db.session.commit()

def update_science():
    app = scheduler.app
    app.logger.info("Updating science stats")

def update_ml():
    from .database import Prediction
    app = scheduler.app
    app.logger.info("Updating ml stats")
    
    with app.app_context():
        # clear out previous top predictions and store new onew        
        MLStat.query.delete()
        TopPrediction.query.delete()

        cranks = get_cranks()
        seen = {}
        for crank in cranks:
            if crank.crank in seen:
                continue
            seen[crank.crank] = 1

            #statistics about training/test data
            train_crystal_score_mean = float(db.session.query(func.avg(TrainingRun._out_crystalscore)).filter_by(dataset=crank.crank).scalar())
            train_length = float(db.session.query(func.count(TrainingRun._out_crystalscore)).filter_by(dataset=crank.crank).scalar())

            # do more training stuff
            try:
                pred_crystal_score_mean = float(db.session.query(func.avg(Prediction.predicted_out)).filter_by(dataset=crank.crank).scalar())
            except:
                pred_crystal_score_mean = 0
                
            #statistics about submissions
            subs = get_submissions(crank.crank)            
            runs = defaultdict(list)
            
            app.logger.info("Retrieved %d submissions for %s" % (len(subs), crank.crank))
            app.logger.info("Train mean: %.2f #train runs:%d Predicted mean: %.2f" % ( train_crystal_score_mean, train_length, pred_crystal_score_mean))

            # aggregate predictions across runs
            # recipe from https://stats.stackexchange.com/questions/15979/how-to-find-confidence-intervals-for-ratings
            for sub in subs:
                for r in sub.rows:
                    name = "%s/%s" % (crank.crank,r.name)
                    smoothed_score = r.score * r.predicted_out + (1 - r.score) * train_crystal_score_mean
                    smoothed_score = r.predicted_out #overwriting since for now, model posteriors are heavily skewed #FIXME
                    runs[name].append((smoothed_score,r))
                    

            # compute smoothed prediction by taking
            h = []
            DISCOUNT = 0.005 # picked out of a hat, a weight of 1 would give equal weight to training mean for only one entry
            TOP_PREDICTION_LIMIT = 25
            
            for name in runs:
                predictions = runs[name]
                num_subs = len(predictions)
                mean = sum([x[0] for x in predictions ]) / num_subs

                weight = num_subs / (num_subs + DISCOUNT)                
                score = weight * mean + (1 - weight) * train_crystal_score_mean
                heapq.heappush(h, (score, num_subs, predictions[0][1].dataset, predictions[0][1].name))


            # now insert the TOP_PREDICTION_LIMIT predictions into the DB
            for r in heapq.nlargest(TOP_PREDICTION_LIMIT, h):
                x = TopPrediction(predicted_out=r[0],
                                  num_subs=r[1],
                                  dataset=r[2],                                  
                                  name=r[3],
                )
                app.logger.info(x)
                db.session.add(x)

            # finally, store off the statistics
            db.session.add(MLStat(crank=crank.crank,
                                  upload_date    = crank.created,
                                  train_mean     = train_crystal_score_mean,
                                  num_train_rows = train_length,
                                  pred_mean      = pred_crystal_score_mean
            )
            )
            #end crank
        db.session.commit()


@bp.route('/dashboard', methods=('GET','POST'))
def dashboard():
    if request.method == 'POST':
        if 'update' in request.form:
            flash("Refreshing stats...")
            job1 = scheduler.add_job(func=update_science, args=[], id = 'update_science')
            job2 = scheduler.add_job(func=update_auto, args=[], id = 'update_auto')
            job3 = scheduler.add_job(func=update_ml, args=[], id = 'update_ml')        
        else:
            flash("Unknown button!")

        seconds=2
        flash("Kicked off job {}.Sleeping for {} seconds to refresh".format(job1,seconds))
        time.sleep(seconds)

    auto_table    = AutomationTable(AutomationStat.query.order_by(AutomationStat.upload_date.desc()).all())
    science_table      = ScienceTable(ScienceStat.query.order_by(ScienceStat.upload_date.desc()).all())
    ml_table = MLTable(MLStat.query.order_by(MLStat.upload_date.desc()).all())
    top_table = TopPredictionTable(TopPrediction.query.order_by(TopPrediction.created.desc()).all())
    return render_template('dashboard.html',science_table=science_table,auto_table=auto_table,ml_table=ml_table, top_table=top_table, top_n=TOP_PREDICTION_LIMIT)

