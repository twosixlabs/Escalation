import pandas as pd
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def get_current_crank():
    db = get_db()
    res=db.execute('SELECT crank FROM cranks WHERE current="TRUE"').fetchone()
    return res['crank']
    
def get_cranks():
    db = get_db()
    cranks = db.execute("SELECT DISTINCT Crank FROM Cranks ORDER by Crank DESC").fetchall()
    return [ x['crank'] for x in cranks]

def get_submissions(crank='all'):
    db = get_db()
    if crank != 'all':
        query = "SELECT id, Username, Expname, Crank, Filename, Notes, Created FROM Submission WHERE Crank = '%s' ORDER BY Created DESC" % crank
    else:
        query = "SELECT id, username, Expname, Crank, Filename, Notes, Created FROM Submission ORDER BY Created DESC"

    return db.execute(query).fetchall()

def set_stateset(set_id):
    db = get_db()
    #expire all other current cranks since we're updating to this one
    db.execute('UPDATE Cranks SET Current = "FALSE" WHERE Current = "TRUE"')
    db.execute("UPDATE Cranks SET Current = 'TRUE' WHERE id='%s'" % set_id)
    res = db.execute("SELECT * FROM Cranks WHERE id='%s'" % set_id).fetchone()

    
    df = pd.read_csv(res['filename'],dtype = {'dataset': str,'name': str,'_rxn_M_inorganic': str,'_rxn_M_organic': str},comment='#')

    db.execute("DELETE FROM Stateset")
    
    for i, r in df.iterrows():
        db.execute('INSERT INTO Stateset (crank,stateset,dataset, name, _rxn_M_inorganic, _rxn_M_organic)'
                   'VALUES (?,?,?,?,?,?)',
                   (res['crank'],
                    res['stateset'],
                    r['dataset'],
                    r['name'],
                    r['_rxn_M_inorganic'],
                    r['_rxn_M_organic'])
                   )
    db.commit()
    return len(df)

def add_stateset(crank, stateset,filename,githash,username):
    db = get_db()
    
    #expire all other current cranks since we're updating to this one
    db.execute('UPDATE Cranks SET Current = "FALSE" WHERE Current = "TRUE"')
            
    #insert new entry
    db.execute(
        'INSERT INTO Cranks (Crank,Stateset,Filename,Githash,Username,Current)'
        'VALUES (?,?,?,?,?,?)',
        (crank,
         stateset,
         filename, #not outfile since thats absolute path
         githash,
         username,
         "TRUE") #true is current
    )


    df = pd.read_csv(filename,dtype = {'dataset': str,'name': str,'_rxn_M_inorganic': str,'_rxn_M_organic': str},comment='#')
    db.execute("DELETE FROM Stateset")
    for i, r in df.iterrows():
        db.execute('INSERT INTO Stateset (crank,stateset,dataset, name, _rxn_M_inorganic, _rxn_M_organic)'
                   'VALUES (?,?,?,?,?,?)',
                   (crank,
                    stateset,
                    r['dataset'],
                    r['name'],
                    r['_rxn_M_inorganic'],
                    r['_rxn_M_organic'])
                   )
    db.commit()
    return len(df)

def get_stateset(id=None):
    db = get_db()
    if id:
        return db.execute("SELECT * FROM Cranks WHERE id='%s'" % id).fetchone()
    else:
        return db.execute("SELECT * FROM Cranks WHERE Current='TRUE'").fetchall()    

def get_cranks():
    db = get_db()
    return db.execute("SELECT * FROM Cranks ORDER by Created DESC").fetchall()

def get_unique_cranks():
    db = get_db()
    return [x['crank'] for x in db.execute("SELECT DISTINCT Crank FROM Cranks ORDER by Created DESC").fetchall()]

def is_stateset_stored(stateset):
    db = get_db()    
    #check if row already in table
    row=db.execute("SELECT Created FROM Cranks WHERE Stateset='%s'" % stateset).fetchone()
    if row != None:
        return "Stateset %s already entered into db on %s" % (stateset,row['Created'].strftime("%Y-%m-%d"))
    else:
        return None

def add_submission(username,expname,crank,filename,notes):
    db = get_db()
    db.execute(
        'INSERT INTO Submission (Username, Expname,Crank, Filename,Notes) VALUES (?,?, ?, ?, ?)',
        (username,
         expname,
         crank,
        filename,
         notes)
    )
    db.commit()
            
def is_row_in_stateset(row):
    db = get_db()
    res = db.execute("SELECT * FROM Stateset").fetchall()
    res=db.execute("SELECT dataset FROM Stateset WHERE dataset='%s' AND name='%s' AND _rxn_M_inorganic='%s' AND _rxn_M_organic='%s'" %
                (row['dataset'],
                 row['name'],
                 row['_rxn_M_inorganic'],
                 row['_rxn_M_organic']
                )
     ).fetchone()
    return res != None
               
        
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')        

