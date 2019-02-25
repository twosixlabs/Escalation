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
    res=db.execute('SELECT crank FROM cranks WHERE current="TRUE"').fetchall()
    return [r['crank'] for r in res]
    
def set_current_crank():
    db = get_db()
    db.execute('UPDATE cranks SET current = "TRUE" WHERE current = "TRUE"')    

def set_stateset(crank, stateset,filename,githash,username):
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


    df = pd.read_csv(filename,comment='#')
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

def get_cranks():
    db = get_db()
    return db.execute("SELECT * FROM Cranks ORDER by Created DESC").fetchall()

def is_stateset_stored(stateset):
    db = get_db()    
    #check if row already in table
    row=db.execute("SELECT Created FROM Cranks WHERE Stateset='%s'" % stateset).fetchone()
    if row != None:
        return "Stateset %s already entered into db on %s" % (stateset,row['Created'].strftime("%Y-%m-%d"))
    else:
        return None

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')        

