import csv
import os

from flask import current_app as app
import numpy as np
from sqlalchemy import and_, sql, text, func
from sqlalchemy.orm import column_property

from escalation import db, PERSISTENT_STORAGE


# Leaderboard statistics

class FeatureImportance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(128))
    heldout_chem = db.Column(db.Boolean)  # did you hold out by chemical?
    crank = db.Column(db.String(64))
    notes = db.Column(db.Text)
    run_id = db.Column(db.String(128))  # string to tie back to a particulary entry (such as in test harness)
    rows = db.relationship('FeatureImportanceValue', backref='entry',
                           lazy='dynamic')  # set of (feature name/weight) pairs
    created = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())


# todo add FeatureSet

class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    desc = db.Column(db.Text)
    created = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())


class FeatureImportanceValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feat_id = db.Column(db.Integer, db.ForeignKey('feature.id'))
    entry_id = db.Column(db.Integer, db.ForeignKey('feature_importance.id'))
    rank = db.Column(db.Integer)
    weight = db.Column(db.Float)


class LeaderBoard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(64))
    githash = db.Column(db.String(64))
    run_id = db.Column(db.String(64))
    created = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())
    model_name = db.Column(db.String(64))
    model_author = db.Column(db.String(64))
    accuracy = db.Column(db.Float)
    balanced_accuracy = db.Column(db.Float)
    auc_score = db.Column(db.Float)
    average_precision = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    samples_in_train = db.Column(db.Integer)
    samples_in_test = db.Column(db.Integer)
    model_description = db.Column(db.Text)
    column_predicted = db.Column(db.String(64))
    num_features_used = db.Column(db.Integer)
    data_and_split_description = db.Column(db.Text)
    normalized = db.Column(db.Boolean)
    num_features_normalized = db.Column(db.Integer)
    feature_extraction = db.Column(db.Boolean)
    was_untested_data_predicted = db.Column(db.Boolean)
    leave_one_out_id = db.Column(db.String(64))
    test_group = db.Column(db.String(64))


#####################
# Dashboard classes #
#####################

class AutomationStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crank = db.Column(db.String(64))
    upload_date = db.Column(db.DateTime(timezone=True))
    num_runs = db.Column(db.Integer, default=0)
    num_uploads = db.Column(db.Integer, default=0)
    num_distinct = db.Column(db.Integer, default=0)


class ScienceStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amine = db.Column(db.String(256))
    success = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=1)
    ratio = column_property(success / total)


class MLStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crank = db.Column(db.String(64))
    upload_date = db.Column(db.DateTime(timezone=True))
    train_mean = db.Column(db.Float, default=0)
    num_train_rows = db.Column(db.Integer, default=0)
    pred_mean = db.Column(db.Float, default=0)


# reproducibility of experiments (from Alex)
class ReproducibilityStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inorganic = db.Column(db.Float)
    organic = db.Column(db.Float)
    acid = db.Column(db.Float)
    temp = db.Column(db.Float)
    size = db.Column(db.Integer)
    score = db.Column(db.Float)
    repo = db.Column(db.Float)


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    expname = db.Column(db.String(64))
    crank = db.Column(db.String(64))
    githash = db.Column(db.String(7))
    notes = db.Column(db.Text)
    created = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())
    rows = db.relationship('Prediction', backref='entry', lazy='dynamic')

    def __repr__(self):
        return '<Submission {} {} {} {}>'.format(self.id, self.username, self.expname, self.crank, self.notes[:10])


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sub_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    name = db.Column(db.String(64))
    dataset = db.Column(db.String(64))
    predicted_out = db.Column(db.Integer)
    score = db.Column(db.Float)

    def __repr__(self):
        return '<Prediction {} {} name={} out={}>'.format(self.id, self.dataset, self.name, self.predicted_out)


class TrainingRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset = db.Column(db.String(64))
    name = db.Column(db.String(64))
    _rxn_M_inorganic = db.Column(db.Float)
    _rxn_M_organic = db.Column(db.Float)
    _rxn_M_acid = db.Column(db.Float)
    _rxn_temperatureC_actual_bulk = db.Column(db.Float)
    _out_crystalscore = db.Column(db.Integer)
    inchikey = db.Column(db.String(128))
    githash = db.Column(db.String(7))

    def __repr__(self):
        return "<Training Run {} {} {} {} {}".format(self.id, self.name, self.dataset, self._out_crystalscore,
                                                     self._rxn_M_inorganic, self._rxn_M_organic, self._rxn_M_acid,
                                                     self.inchikey)


class Crank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crank = db.Column(db.String(64))
    githash = db.Column(db.String(7))  # git commit of stateset file in versioned-data
    username = db.Column(db.String(64))
    num_runs = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    created = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())
    upload_filename = db.Column(db.String(256))  # uploaded file name for comparison
    train_filename = db.Column(db.String(256))  # perovskitedata filename
    num_training_rows = db.Column(db.Integer)

    def __repr__(self):
        return '<Crank {} {} {} {}>'.format(self.crank, self.githash, self.active, self.created)


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    githash = db.Column(db.String(7))
    dataset = db.Column(db.String(11))
    name = db.Column(db.String(256))
    _rxn_M_inorganic = db.Column(db.Float)
    _rxn_M_organic = db.Column(db.Float)
    _rxn_M_acid = db.Column(db.Float)

    def __repr__(self):
        return '<Run {} {} {} {} {}>'.format(self.dataset, self.name, self._rxn_M_inorganic, self._rxn_M_organic,
                                             self._rxn_M_acid)


class Chemical(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())
    inchi = db.Column(db.String(512))
    common_name = db.Column(db.String(512))
    abbrev = db.Column(db.String(128))

    def __repr__(self):
        return "<Chemical {} {} {}>".format(self.inchi, self.common_name, self.abbrev)


def create_db():
    from sqlalchemy import create_engine
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    """Clear the existing data and create new tables."""
    try:
        Crank.__table__.drop(engine)
        Run.__table__.drop(engine)
        Submission.__table__.drop(engine)
        Prediction.__table__.drop(engine)
        TrainingRun.__table__.drop(engine)
    except:
        print("Problem deleting tables, may be ok?")
    db.create_all()


def delete_db():
    Run.query.delete()
    TrainingRun.query.delete()
    Prediction.query.delete()
    Submission.query.delete()
    Crank.query.delete()

    LeaderBoard.query.delete()

    AutomationStat.query.delete()
    MLStat.query.delete()
    ScienceStat.query.delete()
    db.session.commit()


def read_in_stateset(filename, crank, githash):
    Run.query.filter(and_(Run.dataset == crank, Run.githash == githash)).delete()
    with open(os.path.join(app.config[PERSISTENT_STORAGE], filename)) as csvfile:
        csvreader = csv.DictReader(filter(lambda row: row[0] != '#', csvfile))
        objs = []
        for r in csvreader:
            objs.append(
                Run(githash=githash, dataset=r['dataset'], name=r['name'], _rxn_M_inorganic=r['_rxn_M_inorganic'],
                    _rxn_M_organic=r['_rxn_M_organic'], _rxn_M_acid=r['_rxn_M_acid']))  # TODO
    db.session.bulk_save_objects(objs)
    db.session.commit()
    app.logger.info("Added %d runs for stateset" % len(objs))
    return len(objs)


def add_stateset(filename, crank, githash, username, orig_filename, train_filename, num_train_rows):
    num_runs = read_in_stateset(filename, crank, githash)

    # retire other entries that have the same crank
    Crank.query.filter_by(crank=crank).update({'active': False})

    db.session.add(Crank(crank=crank, githash=githash, username=username, num_runs=num_runs, active=True,
                         upload_filename=orig_filename, train_filename=train_filename,
                         num_training_rows=num_train_rows))
    db.session.commit()
    return num_runs


def update_crank_status(id=None, value=False):
    Crank.query.filter_by(id=id).update({'active': value})
    db.session.commit()


def is_stateset_stored(crank, githash):
    return Crank.query.filter(Crank.crank == crank).filter(Crank.githash == githash).scalar() is not None


def get_stateset(id=None):
    if id:
        return Crank.query.filter_by(id=id).first().__dict__
    else:
        return [u.__dict__ for u in Crank.query.filter_by(active=True).all()]


def get_cranks():
    return Crank.query.order_by(Crank.created.desc()).all()


def get_unique_cranks():
    return sorted([x[0] for x in db.session.query(Crank.crank).distinct().all()], reverse=True)


def get_cranks_available_for_download():
    """
    Returns sorted list of dicts for an intersection of active cranks with training files we have cached for download
    """
    # select dataset, count(distinct inchikey) from training_run right join crank on crank.crank=training_run.dataset where crank.active=1 group by dataset;
    # inchi_key_counts = db.session.query(TrainingRun.dataset, func.count(func.distinct(TrainingRun.inchikey))).group_by(TrainingRun.dataset).all()
    return_columns = ('crank', 'githash', 'created', 'num_training_rows', 'num_inchi_keys', 'file_path')
    active_crank_results = db.session.query(Crank.crank,
                                            Crank.githash,
                                            Crank.created,
                                            Crank.num_training_rows,
                                            func.count(func.distinct(TrainingRun.inchikey)),
                                            Crank.train_filename). \
        join(TrainingRun, TrainingRun.dataset == Crank.crank). \
        filter(Crank.active == 1). \
        group_by(Crank.crank, Crank.githash, Crank.created, Crank.num_training_rows, Crank.train_filename).all()
    available_cranks = []
    for query_result in active_crank_results:
        crank_dict = dict(zip(return_columns, query_result))
        # look for a matching training data filename
        persistent_file_path = os.path.join(app.config[PERSISTENT_STORAGE], crank_dict['file_path'])
        if os.path.exists(persistent_file_path):
            available_cranks.append(crank_dict)
    return sorted(available_cranks, reverse=True, key=lambda x: x['crank'])


def get_active_cranks():
    return Crank.query.filter_by(active=True).all()


def is_stateset_active(crank, githash):
    # we are disabling githash checking since the logic is not thought through
    # TODO    return db.session.query(Crank.query.filter(and_(Crank.crank == crank,Crank.githash == githash)).exists()).scalar()
    return Crank.query.filter(Crank.crank == crank).filter(Crank.active == True).scalar() is not None


def get_crank(id=None):
    if id:
        return Crank.query.filter_by(id=id).first()
    else:
        return Crank.query.order_by(Crank.created.desc()).all()


def get_rxns(crank, githash, names):
    # TODO speed up if len(names) == len(Run)
    num_names = len(names)
    num_rows = Run.query.filter(Run.dataset == crank).count()
    if num_names == num_rows:
        res = Run.query.filter(Run.dataset == crank).all()
    else:
        res = Run.query.filter(and_(Run.dataset == crank, Run.name.in_(names))).all()  # todo add githash check
        app.logger.info("Returned %d reactions from stateset" % (len(res)))
        # TODO    res = Run.query.filter(and_(Run.githash==githash,Run.dataset == crank, Run.name.in_(names))).all() #disabled for now since the githash logic is not thought through
    d = {}
    for r in res:
        d[r.name] = {'organic': r._rxn_M_organic, 'inorganic': r._rxn_M_inorganic, 'acid': r._rxn_M_acid}
    return d


def remove_submission(sub_id):
    Prediction.query.filter(Prediction.sub_id == sub_id).delete()
    Submission.query.filter(Submission.id == sub_id).delete()
    db.session.commit()
    # how to deal with test harness?


def add_submission(username, expname, crank, githash, rows, notes):
    sub = Submission(username=username, expname=expname, crank=crank, notes=notes, githash=githash)
    db.session.add(sub)
    db.session.flush()

    objs = []
    for row in rows:
        if row['predicted_out'].lower() == "null":
            row['predicted_out'] = 0
        objs.append(
            Prediction(sub_id=sub.id, dataset=row['dataset'], name=row['name'], predicted_out=row['predicted_out'],
                       score=row['score']))
    db.session.bulk_save_objects(objs)
    db.session.commit()
    app.logger.info("Added %d predictions for submission" % len(objs))


def get_submissions(crank='all'):
    if crank == 'all':
        return Submission.query.order_by(Submission.created.desc()).all()
    else:
        return Submission.query.filter_by(crank=crank).order_by(Submission.created.desc()).all()


def get_predictions(id=None):
    if id is None:
        return Prediction.query.all()
    else:
        return [p.__dict__ for p in Prediction.query.filter_by(sub_id=id).all()]


def get_training(dataset='all'):
    if dataset == 'all':
        return TrainingRun.query.all()
    else:
        return TrainingRun.query.filter_by(dataset=dataset).all()


def add_training(filename, githash, crank):
    app.logger.info("Adding training runs")

    TrainingRun.query.filter(TrainingRun.dataset == crank).delete()
    with open(filename) as csvfile:
        csvreader = csv.DictReader(filter(lambda row: row[0] != '#', csvfile))
        objs = []
        for r in csvreader:
            objs.append(TrainingRun(dataset=r['dataset'],
                                    name=r['name'],
                                    githash=githash,
                                    _rxn_M_inorganic=r['_rxn_M_inorganic'],
                                    _rxn_M_organic=r['_rxn_M_organic'],
                                    _rxn_M_acid=r['_rxn_M_acid'],
                                    _out_crystalscore=r['_out_crystalscore'],
                                    inchikey=r['_rxn_organic-inchikey'],
                                    _rxn_temperatureC_actual_bulk=r['_rxn_temperatureC_actual_bulk'],
                                    ))
        db.session.bulk_save_objects(objs)
        db.session.commit()
    number_of_training_rows = len(objs)
    app.logger.info("Added %d training rows" % number_of_training_rows)
    return number_of_training_rows

def get_leaderboard_loo_inchis():
    sql = text('select distinct test_group from leader_board')
    app.logger.info("Getting distinct elements")    
    res = list(db.engine.execute(sql))
    return [ x for x in res if x[0]]
    

def get_leaderboard(loo=True):

    sql = text('select crank, train_filename from crank order by crank desc limit 1')
    res = list(db.engine.execute(sql))
    
    if loo:
        results = []
        #get unique set of loo_ids
        sql  = text('select leave_one_out_id as "loo_id", avg(auc_score) as "auc", avg(average_precision) as "avgp", avg(`precision`) as "prec", avg(recall) as "recall", avg(f1_score) as "f1" from leader_board group by leave_one_out_id')
        sql1 = text('select distinct leave_one_out_id, dataset_name, model_name from leader_board where leave_one_out_id is not null')
        avg_res = list(db.engine.execute(sql))
        id_res = list(db.engine.execute(sql1))
        h={}
        for row in id_res:
            h[row[0]] = row[1:]
        
        for row in avg_res:
            id, auc, avgp, prec, recall, f1  = row
            if not id:
                continue
            crank, model = h[id]
            x = { 'model': model,
                             'crank' : crank,
                             'loo': True,
                             'auc': auc,
                             'avgp': avgp,
                             'prec': prec,
                             'recall':recall,
                             'f1': f1
                }

            results.append(x)
        return results
        
    else:
        sql = text('select dataset_name, model_name, auc_score, average_precision, `precision`, recall, f1_score from leader_board where leave_one_out_id is NULL')
        res = list(db.engine.execute(sql))
        results=[]
        for row in res:

            x = { 'model':  row[1],
                  'crank' : row[0],
                  'loo': False,
                  'auc': row[2],
                  'avgp': row[3],
                  'prec': row[4],
                  'recall':row[5],
                  'f1':  row[6]
                }

            results.append(x)            
        return results
    
def remove_leaderboard(id):
    LeaderBoard.query.filter(LeaderBoard.id == id).delete()
    db.session.commit()


def convert_to_mysql_friendly_number(form_value, num_type):
    """
    Validate submitted values, converting NaNs to None for mysql
    :return:
    """
    if num_type == float:
        converted_value = float(form_value)
    elif num_type == int:
        converted_value = int(form_value)
    else:
        raise ValueError("num_type %s not recognized" % str(num_type))
    # nan not supported by mysql, so use None which is cast to NULL
    if np.isnan(converted_value):
        return None
    return converted_value


def add_leaderboard(form):
    # a mutable dictionary to store form contents after validation/conversion
    formatted_row = {}
    # required form values
    for column in ('dataset', 'githash', 'run_id', 'model_name', 'model_author', 'accuracy', 'balanced_accuracy',
                   'auc_score', 'average_precision', 'f1_score', 'precision', 'recall', 'samples_in_train',
                   'samples_in_test', 'model_description', 'column_predicted', 'num_features_used',
                   'data_and_split_description', 'normalized', 'num_features_normalized', 'feature_extraction',
                   'was_untested_data_predicted'):
        formatted_row[column] = form[column]
        if column not in form:
            return "column '%s' not in form" % column
    # optional form values
    for column in ('leave_one_out_id', 'test_group'):
        if column in form:
            formatted_row[column] = form[column]
    # validate form values
    try:
        for column in (
                'accuracy', 'balanced_accuracy', 'auc_score', 'average_precision', 'f1_score', 'precision', 'recall'):
            try:
                formatted_row[column] = convert_to_mysql_friendly_number(formatted_row[column], float)
            except ValueError:
                return "Row '%s' with value '%s' does not look like a float" % (column, formatted_row[column])

        for column in ('samples_in_train', 'samples_in_test', 'num_features_used', 'num_features_normalized'):
            try:
                formatted_row[column] = convert_to_mysql_friendly_number(formatted_row[column], int)
            except ValueError:
                return "Row '%s' with value '%s' does not look like an int" % (column, formatted_row[column])

        if len(form['githash']) != 7:
            return "git commit '%s' must be 7 chars" % formatted_row['githash']

        row = LeaderBoard(
            dataset_name=formatted_row['dataset'],
            githash=formatted_row['githash'],
            run_id=formatted_row['run_id'],
            model_name=formatted_row['model_name'],
            model_author=formatted_row['model_author'],
            accuracy=formatted_row['accuracy'],
            balanced_accuracy=formatted_row['balanced_accuracy'],
            auc_score=formatted_row['auc_score'],
            average_precision=formatted_row['average_precision'],
            f1_score=formatted_row['f1_score'],
            precision=formatted_row['precision'],
            recall=formatted_row['recall'],
            samples_in_train=formatted_row['samples_in_train'],
            samples_in_test=formatted_row['samples_in_test'],
            model_description=formatted_row['model_description'],
            column_predicted=formatted_row['column_predicted'],
            num_features_used=formatted_row['num_features_used'],
            data_and_split_description=formatted_row['data_and_split_description'],
            normalized=formatted_row['normalized'] == 'True',
            num_features_normalized=formatted_row['num_features_normalized'],
            feature_extraction=formatted_row['feature_extraction'] == 'True',
            was_untested_data_predicted=formatted_row['was_untested_data_predicted'] == 'True',
            leave_one_out_id=formatted_row.get('leave_one_out_id'),
            test_group=formatted_row.get('test_group')
        )
        db.session.add(row)
        db.session.commit()
    except Exception as ex:
        print(ex)

        app.logger.error("Error submitting leaderboard :(")
        return "Unknown error loading db"

    return None


def get_chemicals():
    return Chemical.query.order_by(Chemical.inchi.desc()).all()


def get_chemicals_in_training():
    chems = Chemical.query.order_by(Chemical.common_name.asc()).all()
    training_inchis = [x[0] for x in db.session.query(TrainingRun.inchikey).distinct().all()]
    return [c for c in chems if c.inchi in training_inchis]


def remove_chemical(id):
    Chemical.query.filter(Chemical.id == id).delete()


def is_inchi_stored(inchi):
    return Crank.query.filter(Chemical.inchi == inchi).scalar() is not None


def set_chemical(inchi, common_name, abbrev):
    Chemical.query.filter(Chemical.inchi == inchi).delete()
    db.session.add(Chemical(inchi=inchi, common_name=common_name, abbrev=abbrev))
    db.session.commit()


def get_unique_training_runs():
    sql = text(
        'select distinct name,inchikey,_out_crystalscore,_rxn_M_organic,_rxn_M_inorganic,_rxn_M_acid from training_run')
    result = list(db.engine.execute(sql))
    app.logger.info("Returned %d unique training runs" % len(result))
    return result


def get_perovskites_data():
    sql = text('select crank, train_filename from crank order by crank desc limit 1')
    res = list(db.engine.execute(sql))
    return res[0].crank, res[0].train_filename


def add_feature_analysis(obj):
    # validate
    for form in ('method', 'crank', 'notes', 'chem_heldout', 'all_chem', 'run_id', 'features'):
        if form not in obj:
            return "Must include", form, " in form"

    for x in ('chem_heldout', 'all_chem'):
        for f in obj[x]:
            if 'value' not in obj[x][f]:
                return "%s,%s does not have entry 'value'" % (x, f)
            elif 'rank' not in obj[x][f]:
                return "%s,%s does not have entry 'value'" % (x, f)
            elif len(obj[x][f]['value']) < 3:
                return "%s,%s:does not have 3+ samples" % (x, f)
            elif len(obj[x][f]['rank']) < 3:
                return "%s,%s: does not have 3+ samples" % (x, f)
            elif len(obj[x][f]['rank']) != len(obj[x][f]['value']):
                return "%s,%s: does not have equal length ranks and values" % (x, f)

    allowable_featuree_importance_methods = {'shap', 'bba'}
    if obj.get('method') not in allowable_featuree_importance_methods:
        return "Method should be one of %s" % allowable_featuree_importance_methods

    # add features if new
    heldout_entry = FeatureImportance(method=obj['method'],
                                      crank=obj['crank'],
                                      notes=obj['notes'],
                                      run_id=obj['run_id'],
                                      heldout_chem=True,
                                      )
    general_entry = FeatureImportance(method=obj['method'],
                                      crank=obj['crank'],
                                      notes=obj['notes'],
                                      run_id=obj['run_id'],
                                      heldout_chem=False,
                                      )

    res = FeatureImportance.query.filter(FeatureImportance.method == obj['method']).filter(
        FeatureImportance.crank == obj['crank']).all()
    if res is not None:
        for r in res:
            app.logger.info("Removing existing entry %d for %s %s" % (r.id, r.method, r.crank))
            remove_feature_analysis(r.id)

    db.session.add(heldout_entry)
    db.session.add(general_entry)
    db.session.flush()
    app.logger.info("Created heldout analysis %d and general %d" % (heldout_entry.id, general_entry.id))
    feats = []
    imps = []

    for feat in obj['features']:
        if Feature.query.filter(Feature.name == feat).scalar() is None:
            db.session.add(Feature(name=feat, desc=""))
    db.session.flush()

    ids = {}
    for f in Feature.query.all():
        ids[f.name] = f.id

    heldout_objs = []
    general_objs = []
    for feat, arr in obj['chem_heldout'].items():
        if feat not in ids:
            app.logger.info("Somehow feature %s is not in the db" % feat)
            return "Could not add feature %s to the db" % feat
        varr = arr['value']
        rarr = arr['rank']
        for i, v in enumerate(varr):
            r = rarr[i]
            if int(r) != r or r < 1:
                return "Rank value is not a numeral"
            heldout_objs.append(FeatureImportanceValue(feat_id=ids[feat], entry_id=heldout_entry.id, rank=r, weight=v))

    for feat, arr in obj['all_chem'].items():
        if feat not in ids:
            app.logger.info("Somehow feature %s is not in the db" % feat)
            return "Could not add feature %s to the db" % feat
        varr = arr['value']
        rarr = arr['rank']
        for i, v in enumerate(varr):
            r = rarr[i]
            if int(r) != r or r < 1:
                return "Rank value is not a numeral"
            heldout_objs.append(FeatureImportanceValue(feat_id=ids[feat], entry_id=general_entry.id, rank=r, weight=v))

    db.session.bulk_save_objects(heldout_objs)
    db.session.bulk_save_objects(general_objs)
    db.session.commit()
    app.logger.info("Added analyses for %d features" % (len(obj['all_chem'])))
    return None


def remove_feature_analysis(id=None):
    FeatureImportanceValue.query.filter(FeatureImportanceValue.entry_id == id).delete()
    FeatureImportance.query.filter(FeatureImportance.id == id).delete()
    db.session.commit()


def get_feature_analysis(id='all'):
    return FeatureImportance.query.all()


def get_features():
    return Feature.query.order_by(Feature.name.desc()).all()
