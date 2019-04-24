from flask import (
    Blueprint, flash, g, redirect, render_template, request
)
from flask import current_app
from escalation import scheduler, db
from collections import defaultdict
from sqlalchemy import text
from sqlalchemy.sql import func

import time
import random
import heapq

#ugh, I know
from . import database
from .database import *
from . import plot

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
        plot.update_uploads_by_crank()
        plot.update_runs_by_crank()
        plot.update_runs_by_month()        
        
def update_science():
    app = scheduler.app
    app.logger.info("Updating science stats")
    with app.app_context():    
        rows = database.get_unique_training_runs()
        #0 name
        #1 inchikey
        #2 _out_crystalscore
        #3 _rxn_M_organic
        #4 _rxn_M_inorganic
        #5 _rxn_M_acid
    
        total = defaultdict(int)
        success = defaultdict(int)
        for r in rows:
            total[r[1]] += 1
            if r[2] == 4:
                success[r[1]] += 1

        ScienceStat.query.delete()
        chemicals={}
        res = database.get_chemicals()
        for r in res:
            chemicals[r.inchi] = r.common_name
        
        for amine in total:
            db.session.add(ScienceStat(amine=chemicals[amine] if amine in chemicals else amine,
                                       success = success[amine],
                                       total = total[amine]
            ))
            app.logger.info("%s: %d %d" % (amine, success[amine],total[amine]))
            db.session.commit()

        plot.update_repo_table()
        plot.update_success_by_amine()
        plot.update_scatter_3d_by_rxn()
        plot.update_feature_importance()
        
def update_ml():
    from .database import Prediction
    app = scheduler.app
    app.logger.info("Updating ml stats")
    
    with app.app_context():
        # clear out previous top predictions and store new onew        
        MLStat.query.delete()

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
        plot.update_results_by_model() #f1_by_model and results_by_model

    
@bp.route('/dashboard', methods=('GET','POST'))
def dashboard():
    curr_inchikey='all'
    
    if request.method == 'POST':
        if 'update' in request.form:
            flash("Refreshing stats...")
            app.logger.info("Refreshing stats")
            job1 = scheduler.add_job(func=update_science, args=[], id = 'update_science')
            job2 = scheduler.add_job(func=update_auto, args=[], id = 'update_auto')
            job3 = scheduler.add_job(func=update_ml, args=[], id = 'update_ml')
            
        elif 'inchikey' in request.form:
            curr_inchikey=request.form['inchikey']
            flash("Updating 3D scatter plot with %s" % request.form['inchikey'])
            plot.update_scatter_3d_by_rxn(request.form['inchikey'])
        elif 'repo_update' in request.form:
            flash("Updating Reproducibility plot with %s" % request.form['inchikey_repo'])
            plot.update_repo_table(inchi=request.form['inchikey_repo'],prec=float(request.form['prec_repo']))
        else:
            flash("Unknown button!")

    auto_table = AutomationStat.query.all()
    sci_table  = ScienceStat.query.all()
    ml_table   = MLStat.query.all()
    repo_table = RepoStat.query.all()
    exp_repo_stats = plot.repo_table_stats() #get the updated summary statistics after calling update_repo_table
    
    return render_template('dashboard.html',
                           sci_table     = sci_table,
                           auto_table    = auto_table,
                           ml_table      = ml_table,
                           leaderboard   = get_leaderboard(),
                           chemicals     = database.get_chemicals_in_training(),
                           curr_inchikey = curr_inchikey,
                           exp_repo_stats= exp_repo_stats,

                           #science
                           success_by_amine   = plot.success_by_amine(),
                           rxn_3d_scatter     = plot.scatter_3d_by_rxn(),
                           feature_importance = plot.feature_importance(),
                           repo_table    = repo_table,
                           
                           #automation
                           uploads_by_crank = plot.uploads_by_crank(),
                           runs_by_crank    = plot.runs_by_crank(),
                           runs_by_month    = plot.runs_by_month(),

                           #ml
                           results_by_model = plot.results_by_model(),
                           results_by_crank = plot.results_by_crank(),
                           f1_by_model = plot.f1_by_model(),
    )



# Old code to compute highest confidence runs in data
#             # aggregate predictions across runs
#             # recipe from https://stats.stackexchange.com/questions/15979/how-to-find-confidence-intervals-for-ratings
#             for sub in subs:
#                 for r in sub.rows:
#                     name = "%s/%s" % (crank.crank,r.name)
#                     smoothed_score = r.score * r.predicted_out + (1 - r.score) * train_crystal_score_mean
#                     smoothed_score = r.predicted_out #overwriting since for now, model posteriors are heavily skewed #FIXME
#                     runs[name].append((smoothed_score,r))
                    

#             # compute smoothed prediction by taking
#             h = []
#             DISCOUNT = 0.005 # picked out of a hat, a weight of 1 would give equal weight to training mean for only one entry
#             TOP_PREDICTION_LIMIT = 25
            
#             for name in runs:
# red_                predictions = runs[name]
#                 num_subs = len(predictions)
#                 mean = sum([x[0] for x in predictions ]) / num_subs

#                 weight = num_subs / (num_subs + DISCOUNT)                
#                 score = weight * mean + (1 - weight) * train_crystal_score_mean
#                 heapq.heappush(h, (score, num_subs, predictions[0][1].dataset, predictions[0][1].name))


#             # now insert the TOP_PREDICTION_LIMIT predictions into the DB
#             for r in heapq.nlargest(TOP_PREDICTION_LIMIT, h):
#                 x = TopPrediction(predicted_out=r[0],
#                                   num_subs=r[1],
#                                   dataset=r[2],                                  
#                                   name=r[3],
#                 )
#                 app.logger.info(x)
#                 db.session.add(x)

