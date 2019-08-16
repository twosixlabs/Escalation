from flask import Blueprint, flash, render_template, request
from escalation import scheduler, db
from collections import defaultdict

# ugh, I know
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
            num_distinct_entries = db.session.query(Prediction.dataset, Prediction.name).filter_by(
                dataset=crank.crank).group_by(Prediction.dataset, Prediction.name).count()

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
        # 0 name
        # 1 inchikey
        # 2 _out_crystalscore
        # 3 _rxn_M_organic
        # 4 _rxn_M_inorganic
        # 5 _rxn_M_acid

        total = defaultdict(int)
        success = defaultdict(int)
        for r in rows:
            total[r[1]] += 1
            if r[2] == 4:
                success[r[1]] += 1

        ScienceStat.query.delete()
        chemicals = {}
        res = database.get_chemicals()
        for r in res:
            chemicals[r.inchi] = r.common_name

        for amine in total:
            db.session.add(ScienceStat(amine=chemicals[amine] if amine in chemicals else amine,
                                       success=success[amine],
                                       total=total[amine]
                                       ))
            app.logger.info("%s: %d %d" % (amine, success[amine], total[amine]))
            db.session.commit()

        plot.update_reproducibility_table()
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

            # statistics about training/test data
            train_crystal_score_mean = float(
                db.session.query(func.avg(TrainingRun._out_crystalscore)).filter_by(dataset=crank.crank).scalar())
            train_length = float(
                db.session.query(func.count(TrainingRun._out_crystalscore)).filter_by(dataset=crank.crank).scalar())

            # do more training stuff
            try:
                pred_crystal_score_mean = float(
                    db.session.query(func.avg(Prediction.predicted_out)).filter_by(dataset=crank.crank).scalar())
            except:
                pred_crystal_score_mean = 0

            # statistics about submissions
            subs = get_submissions(crank.crank)
            runs = defaultdict(list)

            app.logger.info("Retrieved %d submissions for %s" % (len(subs), crank.crank))
            app.logger.info("Train mean: %.2f #train runs:%d Predicted mean: %.2f" % (
            train_crystal_score_mean, train_length, pred_crystal_score_mean))

            # finally, store off the statistics
            db.session.add(MLStat(crank=crank.crank,
                                  upload_date=crank.created,
                                  train_mean=train_crystal_score_mean,
                                  num_train_rows=train_length,
                                  pred_mean=pred_crystal_score_mean
                                  )
                           )
            # end crank
        db.session.commit()
        plot.update_results_by_model()  # f1_by_model and results_by_model


@bp.route('/', methods=('GET', 'POST'))
def dashboard():
    return render_template('dashboard_overview.html',
                           success_by_amine=plot.success_by_amine(),
                           runs_by_crank=plot.runs_by_crank(),
                           results_by_model=plot.results_by_model())


@bp.route('/dashboard/science', methods=('GET', 'POST'))
def dashboard_science():
    curr_inchikey = 'all'
    if request.method == 'POST':
        if 'update' in request.form:
            flash("Refreshing stats...")
            app.logger.info("Refreshing stats")
            job1 = scheduler.add_job(func=update_science, args=[], id='update_science')
        elif 'inchikey' in request.form:
            curr_inchikey = request.form['inchikey']
            flash("Updating 3D scatter plot with %s" % request.form['inchikey'])
            plot.update_scatter_3d_by_rxn(request.form['inchikey'])
        elif 'reproducibility_update' in request.form:
            flash("Updating Reproducibility plot with %s" % request.form['inchikey_repro'])
            plot.update_reproducibility_table(inchi=request.form['inchikey_repro'],
                                              prec=float(request.form['prec_repro']))

    sci_table = ScienceStat.query.all()
    reproducibility_table = ReproducibilityStat.query.all()
    exp_repro_stats = plot.reproducibility_table_stats()

    return render_template('dashboard_science.html',
                           sci_table=sci_table,
                           chemicals=database.get_chemicals_in_training(),
                           curr_inchikey=curr_inchikey,
                           # science
                           success_by_amine=plot.success_by_amine(),
                           rxn_3d_scatter=plot.scatter_3d_by_rxn(),
                           feature_importance=plot.feature_importance(),
                           reproducibility_table=reproducibility_table,
                           exp_repro_stats=exp_repro_stats,
                           )


@bp.route('/dashboard/automation', methods=('GET', 'POST'))
def dashboard_automation():
    if request.method == 'POST' and 'update' in request.form:
        flash("Refreshing stats...")
        app.logger.info("Refreshing stats")
        job2 = scheduler.add_job(func=update_auto, args=[], id='update_auto')

    auto_table = AutomationStat.query.all()
    return render_template('dashboard_automation.html',
                           # automation
                           auto_table=auto_table,
                           uploads_by_crank=plot.uploads_by_crank(),
                           runs_by_crank=plot.runs_by_crank(),
                           runs_by_month=plot.runs_by_month())


@bp.route('/dashboard/ml', methods=('GET', 'POST'))
def dashboard_ml():
    if request.method == 'POST' and 'update' in request.form:
        flash("Refreshing stats...")
        app.logger.info("Refreshing stats")
        job2 = scheduler.add_job(func=update_auto, args=[], id='update_ml')

    ml_table   = MLStat.query.all()
    return render_template('dashboard_ml.html',
                           leaderboard=get_leaderboard(),
                           ml_table=ml_table,
                           results_by_model=plot.results_by_model(),
                           results_by_crank=plot.results_by_crank(),
                           f1_by_model=plot.f1_by_model())
