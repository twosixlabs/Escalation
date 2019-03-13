from escalation import db
from escalation import Submission, Crank, Run
from sqlalchemy import and_
from flask import current_app, g
import csv

def read_in_stateset(filename,crank,stateset):
    Run.query.filter_by(stateset=stateset).delete()    
    current_app.logger.info("reading in csv")        
    with open(filename) as csvfile:
        csvreader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile))
        num_rows = 0
        objs=[]
        for r in csvreader:
            num_rows+=1
            objs.append(Run(crank=crank,stateset=stateset,dataset=r['dataset'],name=r['name'],_rxn_M_inorganic=r['_rxn_M_inorganic'],_rxn_M_organic=r['_rxn_M_organic']))
    current_app.logger.info("adding objects")        
    db.session.bulk_save_objects(objs)
    db.session.commit()
    current_app.logger.info("Added objects")    
    return num_rows
    
def is_stateset_stored(stateset):
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

def add_submission(username,expname,crank,content,notes):
    db.session.add(Submission(username=username,expname=expname,crank=crank,content=content,notes=notes))
    db.session.commit()

def get_submissions(crank='all'):
    if crank == 'all':
        return Submission.query.all()
    else:
        return Submission.query.filter_by(crank=crank).all()
