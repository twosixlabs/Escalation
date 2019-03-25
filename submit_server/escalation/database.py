from escalation import db
from sqlalchemy import and_, sql, create_engine
from sqlalchemy.orm import deferred
from flask import current_app, g
from flask_table import Table, Col, DateCol
import csv

class AutomationStat(db.Model):
    id          = db.Column(db.Integer,primary_key=True)
    crank       = db.Column(db.String(64))
    upload_date = db.Column(db.DateTime(timezone=True))
    num_runs    = db.Column(db.Integer,default=0)
    num_uploads = db.Column(db.Integer,default=0)
    num_distinct= db.Column(db.Integer,default=0)
    
class AutomationTable(Table):
    crank       = Col('Crank')
    upload_date = DateCol('Upload Date',date_format='short')
    num_runs    = Col('Number of Runs')
    num_uploads = Col('Number of Uploads')
    num_distinct= Col('Number of Unique Entries')
    

class ScienceStat(db.Model):
    id          = db.Column(db.Integer,primary_key=True)
    crank       = db.Column(db.String(64))
    upload_date = db.Column(db.DateTime(timezone=True))
    
class ScienceTable(Table):
    crank       = Col('Crank')
        

class TopPrediction(db.Model):
    id               = db.Column(db.Integer,primary_key=True)
    name             = db.Column(db.String(64))
    dataset          = db.Column(db.String(64))
    predicted_out    = db.Column(db.Float)
    num_subs         = db.Column(db.Integer)
    
    def __repr__(self):
        return "<TopPrediction {0} {1} {2} {3:.2f} {4}".format(self.id, self.dataset,self.name,self.predicted_out,self.num_subs)

class TopPredictionTable(Table):
    dataset       = Col('Crank')
    name          = Col('Run ID')    
    predicted_out = Col('Predicted Score')
    num_subs      = Col('Confidence')
    
class MLStat(db.Model):
    id             = db.Column(db.Integer,primary_key=True)
    crank          = db.Column(db.String(64))
    upload_date    = db.Column(db.DateTime(timezone=True))
    train_mean     = db.Column(db.Float, default=0)
    num_train_rows = db.Column(db.Integer,default=0)
    pred_mean      = db.Column(db.Float,default=0)

class MLTable(Table):
    crank       = Col('Crank')
    upload_date = DateCol('Upload Date',date_format='short')
    train_mean  = Col('Avg. Training Crystal Score')
    num_train_rows = Col('Number of Rows in Training')
    pred_mean = Col('Avg. Predicted Crystal Score')

    

    
class Submission(db.Model):
    id       = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64))
    expname  = db.Column(db.String(64))
    crank    = db.Column(db.String(64))
    notes    = db.Column(db.Text)
    created  = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())
    rows     = db.relationship('Prediction', backref='entry', lazy='dynamic')

    def __repr__(self):
        return '<Submission {} {} {} {}>'.format(self.id,self.username,self.expname,self.crank,self.notes[:10]) 

class Prediction(db.Model):
    id              = db.Column(db.Integer,primary_key=True)
    sub_id          = db.Column(db.Integer, db.ForeignKey('submission.id'))
    name            = db.Column(db.String(64))
    dataset         = db.Column(db.String(64))    
    predicted_out   = db.Column(db.Integer)
    score           = db.Column(db.Float)

    def __repr__(self):
        return '<Prediction {} {} name={} out={}>'.format(self.id, self.dataset, self.name, self.predicted_out)

class TrainingRun(db.Model):
    id                = db.Column(db.Integer,primary_key=True)
    dataset           = db.Column(db.String(64))
    name              = db.Column(db.String(64))    
    _rxn_M_inorganic  = db.Column(db.Float)
    _rxn_M_organic    = db.Column(db.Float)
    _out_crystalscore = db.Column(db.Integer)
    inchikey          = db.Column(db.String(128))
    
    def __repr__(self):
        return "<Training Run {} {} {} {}".format(self.id,self.name,self.dataset,self._out_crystalscore,self._rxn_M_inorganic,self._rxn_M_organic,self.inchikey)
    
class Crank(db.Model):
    id       = db.Column(db.Integer,primary_key=True)
    crank    = db.Column(db.String(64))    
    stateset = db.Column(db.String(11))
    githash  = db.Column(db.String(7))    #git commit of stateset file
    username = db.Column(db.String(64))
    num_runs = db.Column(db.Integer)    
    current  = db.Column(db.Boolean)
    created  = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())

    def  __repr__(self):
        return '<Crank {} {} {} {}>'.format(self.crank,self.stateset,self.githash,self.current)

class Run(db.Model):
    id               = db.Column(db.Integer,primary_key=True)
    crank            = db.Column(db.String(64))    
    stateset         = db.Column(db.String(11))
    dataset          = db.Column(db.String(11))    
    name             = db.Column(db.String(256))
    _rxn_M_inorganic = db.Column(db.Float)
    _rxn_M_organic   = db.Column(db.Float)           

    def __repr__(self):
        return '<Run {} {} {} {}>'.format(self.stateset,self.name,self._rxn_M_inorganic,self._rxn_M_organic)

def create_db():
    from sqlalchemy import create_engine
    engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
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
    Prediction.query.delete()    
    Submission.query.delete()
    Crank.query.delete()
    db.session.commit()


def read_in_stateset(filename,crank,stateset):
    Run.query.filter_by(stateset=stateset).delete()
    with open(filename) as csvfile:
        csvreader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile))
        objs=[]
        for r in csvreader:
            objs.append(Run(crank=crank,stateset=stateset,dataset=r['dataset'],name=r['name'],_rxn_M_inorganic=r['_rxn_M_inorganic'],_rxn_M_organic=r['_rxn_M_organic']))
    db.session.bulk_save_objects(objs)
    db.session.commit()
    current_app.logger.info(" Added %d runs for stateset" % len(objs))
    return len(objs)
    
def is_stateset_stored(stateset):
    return False
    return Crank.query.filter_by(stateset=stateset).scalar() is not None

def add_stateset(crank,stateset,filename,githash,username):
    Crank.query.filter_by(current=True).update({'current':False})
    num_runs= read_in_stateset(filename,crank,stateset)
    db.session.add(Crank(crank=crank,stateset=stateset,githash=githash,username=username,num_runs=num_runs,current=True))
    db.session.commit()
    return num_runs

def set_stateset(id=None):
    Crank.query.filter_by(current=True).update({'current':False})
    Crank.query.filter_by(id=id).update({'current':True})
    db.session.commit()
    
def get_stateset(id=None):
    if id:
        return Crank.query.filter_by(id=id).first().__dict__
    else:
        return [u.__dict__ for u in Crank.query.filter_by(current=True).all()]

    
def get_cranks():
    return Crank.query.order_by(Crank.created.desc()).all()
    
def get_unique_cranks():
    return [x[0] for x in db.session.query(Crank.crank).distinct().order_by(Crank.created.desc())]

def get_current_crank():
    return Crank.query.filter_by(current=True).first()

def get_crank(id=None):
    if id:
        return Crank.query.filter_by(id=id).first()
    else:
        return Crank.query.order_by(Crank.created.desc()).all()

def get_rxns(stateset,names):
    res = Run.query.filter(and_(Run.stateset == stateset, Run.name.in_(names))).all()
    current_app.logger.info("Returned %d reactions from stateset" % (len(res)))
    d={}
    for r in res:
        d[r.name] = {'organic':r._rxn_M_organic,'inorganic':r._rxn_M_inorganic}
    return d

def add_submission(username,expname,crank,rows,notes):
    sub=Submission(username=username,expname=expname,crank=crank,notes=notes)
    db.session.add(sub)
    db.session.flush()
    
    objs=[]
    for row in rows:
        objs.append(Prediction(sub_id=sub.id,dataset=row['dataset'],name=row['name'],predicted_out=row['predicted_out'],score=row['score']))
    db.session.bulk_save_objects(objs)
    db.session.commit()
    current_app.logger.info("Added %d predictions for submission" % len(objs))
    
def get_submissions(crank='all'):
    if crank == 'all':
        return Submission.query.order_by(Submission.created.desc()).limit(10).all()
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
    
def add_training(crank,stateset,filename,githash,username):
    with open(filename) as csvfile:
        csvreader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile))
        objs=[]
        for r in csvreader:
            objs.append(TrainingRun(dataset=r['dataset'],name=r['name'],_rxn_M_inorganic=r['_rxn_M_inorganic'],_rxn_M_organic=r['_rxn_M_organic'],_out_crystalscore=r['_out_crystalscore'],inchikey=r['_rxn_organic-inchikey']))
    db.session.bulk_save_objects(objs)
    db.session.commit()
    current_app.logger.info("Added %d training runs" % len(objs))    
    return len(objs)
