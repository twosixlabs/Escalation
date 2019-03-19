from escalation import db
from sqlalchemy import and_, sql, create_engine
from sqlalchemy.orm import deferred
from flask import current_app, g
import csv

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
    except:
        print("Problem deleting tables, may be ok?")
    db.create_all()

def delete_db():
    Run.query.delete()
    Prediction.query.delete()    
    Submission.query.delete()
    Crank.query.delete()    

def insert_demo_data():
    delete_db()
    db.session.add(Submission(username='snovot',expname='name', crank='0001',notes='test test test',id=1))
    db.session.add(Submission(username='snovot',expname='name1',crank='0002',notes='test test test',id=2))
    db.session.add(Submission(username='snovot',expname='name2',crank='0002',notes='test test test',id=3))
    
    db.session.add(Prediction(id=1,sub_id=1,name=1,dataset='12345678901',predicted_out=1,score=0.5))
    db.session.add(Prediction(id=2,sub_id=1,name=2,dataset='12345678901',predicted_out=2,score=0.5))
    db.session.add(Prediction(id=3,sub_id=1,name=3,dataset='12345678901',predicted_out=2,score=0.5))
    db.session.add(Prediction(id=4,sub_id=1,name=4,dataset='12345678901',predicted_out=4,score=0.5))
    db.session.add(Prediction(id=5,sub_id=2,name=1,dataset='aaaa5678901',predicted_out=4,score=0.9))
    db.session.add(Prediction(id=6,sub_id=2,name=2,dataset='aaaa5678901',predicted_out=4,score=0.1))
    db.session.add(Prediction(id=7,sub_id=2,name=3,dataset='aaaa5678901',predicted_out=4,score=0.2))
    db.session.add(Prediction(id=8,sub_id=2,name=4,dataset='aaaa5678901',predicted_out=4,score=0.4))
    db.session.add(Prediction(id=9,sub_id=3,name=1,dataset='bbbb5678901',predicted_out=2,score=0.2))
    db.session.add(Prediction(id=10,sub_id=3,name=2,dataset='bbbb5678901',predicted_out=2,score=0.5))
    db.session.add(Prediction(id=11,sub_id=3,name=3,dataset='bbbb5678901',predicted_out=2,score=0.05))
    db.session.add(Prediction(id=12,sub_id=3,name=4,dataset='bbbb5678901',predicted_out=2,score=1))
    db.session.add(Crank(crank='0002', stateset='bbbb5678901', githash='abc1236', num_runs=9,username='snovot', current=True))
    db.session.add(Crank(crank='0002', stateset='aaaa5678901', githash='abc1235', num_runs=9,username='snovot', current=False))    
    db.session.add(Crank(crank='0001', stateset='12345678901', githash='abc1234', num_runs=9,username='snovot', current=False))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='0',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='1',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='2',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='3',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='4',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='5',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='6',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='7',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='8',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='aaaa5678901',name='9',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='0',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='1',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='2',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='3',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='4',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='5',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='6',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='7',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='8',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',name='9',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='bbbb5678901',name='0',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='12345678901',name='1',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='12345678901',name='2',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='12345678901',name='3',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='12345678901',name='4',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='12345678901',name='5',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='12345678901',name='6',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='12345678901',name='7',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='12345678901',name='8',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0001',stateset='12345678901',name='9',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))    
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
        return Submission.query.all()
    else:
        return Submission.query.filter_by(crank=crank).all()

def get_predictions(id=None):
    if id is None:
        return Prediction.query.all()
    else:
        return [p.__dict__ for p in Prediction.query.filter_by(sub_id=id).all()]

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
