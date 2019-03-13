import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import sql
from sqlalchemy.orm import deferred
import click
import logging
from logging.handlers import RotatingFileHandler

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    #        DATABASE=os.path.join(app.instance_path, 'escalation.sqlite'),
    UPLOAD_FOLDER = os.path.join(app.instance_path,'submissions'),
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(app.instance_path,'escalation.sqlite'),
    #32 MB max upload
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024,
    ADMIN_KEY='secret',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
    
# ensure the instance folder exists
try:
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
except OSError:
    pass

db = SQLAlchemy(app)

class Submission(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64))
    expname = db.Column(db.String(64))
    crank = db.Column(db.String(64))
    content = deferred(db.Column(db.Text()))
    notes = db.Column(db.Text)
    created = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())
    def __repr__(self):
        return '<Submission {} {} {} {}>'.format(self.id,self.username,self.expname,self.crank,self.content[0:10]) 

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
    id = db.Column(db.Integer,primary_key=True)
    crank    = db.Column(db.String(64))    
    stateset = db.Column(db.String(11))
    dataset = db.Column(db.String(11))    
    name = db.Column(db.String(256))
    _rxn_M_inorganic = db.Column(db.Float)
    _rxn_M_organic = db.Column(db.Float)           

    def __repr__(self):
        return '<Run {} {} {} {}>'.format(self.stateset,self.name,self._rxn_M_inorganic,self._rxn_M_organic)

@app.cli.command()
def init_db():
    from sqlalchemy import create_engine
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    """Clear the existing data and create new tables."""
    try:
        Crank.__table__.drop(engine)
        Run.__table__.drop(engine)
        Submission.__table__.drop(engine)
    except:
        print("Problem deleting tables, may be ok?")
    db.create_all()
    click.echo('Initialized the database.')   

    
def delete_db():
    Run.query.delete()
    Submission.query.delete()
    Crank.query.delete()    

def insert_demo_data():
    delete_db()
    content1= b"""# USERNAME: snovotney
dataset,name,_rxn_M_inorganic,_rxn_M_organic,predicted_out,score
12345678901,1,0,0,4,1
12345678901,2,0,0,4,0.4
12345678901,3,0,0,4,0.5
12345678901,4,0,0,4,0.4
"""
    content2=b"""# USERNAME: snovotney
dataset,name,_rxn_M_inorganic,_rxn_M_organic,predicted_out,score
bbbb5678901,1,0,0,4,1
bbbb5678901,2,0,0,4,0.4
bbbb5678901,3,0,0,4,0.5
bbbb5678901,4,0,0,4,0.4
"""
    content3=b"""# USERNAME: snovotney
dataset,name,_rxn_M_inorganic,_rxn_M_organic,predicted_out,score
bbbb5678901,1,0,0,4,1
bbbb5678901,2,0,0,2,10
bbbb5678901,4,0,0,4,0.4
"""
    
    db.session.add(Crank(crank='0002', stateset='bbbb5678901', githash='abc1236', num_runs=9,username='snovot', current=True))
    db.session.add(Crank(crank='0002', stateset='aaaa5678901', githash='abc1235', num_runs=9,username='snovot', current=False))    
    db.session.add(Crank(crank='0001', stateset='12345678901', githash='abc1234', num_runs=9,username='snovot', current=False))
    db.session.add(Submission(username='snovot',expname='name',crank='0001',content=content1,notes='test test test'))
    db.session.add(Submission(username='snovot',expname='name1',crank='0002',content=content2,notes='test test test'))
    db.session.add(Submission(username='snovot',expname='name2',crank='0002',content=content3,notes='test test test'))
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
    click.echo("Added demo data")

@app.cli.command('demo-db')
def demo_data():
    insert_demo_data()

@app.cli.command('reset-db')
def reset_db():
    delete_db()

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

@app.route('/links')
def links():
    return render_template('links.html')

from . import submission
from . import view
from . import admin
app.register_blueprint(submission.bp)
app.register_blueprint(view.bp)
app.register_blueprint(admin.bp)            


if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/escalation.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('ESCALATion started')    

app.logger.info("Writing to %s" % app.config['SQLALCHEMY_DATABASE_URI'])
