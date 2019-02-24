from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from escalation.db import get_db, set_current_crank, get_current_crank

def validate_entry(data):
    if data['admincode'] != app.config['ADMIN_KEY']:
        return "Your Admin code is incorrect"
    if len(data['crank']) != 4 or not data['crank'].isdigit():
        return "Crank length is not of format '0000'"
    if len(data['stateset']) != 11:
        return "Stateset hash is not 11 characters (current length is %d)" % len(data['stateset'])
    if len(data['gitcommit']) != 7:
        return "Git commit hash is not 7 characters (current length is %d)" % len(data['gitcommit'])
    if not data['length'].isdigit():
        return "Stateset length doesn't look like an int"
    if int(data['length']) < 1:
        return "Stateset length is 0 or less"
    return None


    
bp = Blueprint('admin',__name__)
@bp.route('/admin', methods=('GET','POST'))
def admin():
    db = get_db()
    error = None
    
    if request.method == 'POST':
        for key in ('crank','stateset','length','gitcommit','admincode'):
            session[key] = request.form[key]

        error = validate_entry(request.form)

        if error == None:
            #check if row already in table
            res=db.execute('SELECT Created FROM Cranks WHERE Crank=? AND Stateset=? AND Length=? AND Gitcommit=?',
                           (request.form['crank'],
                            request.form['stateset'],
                            request.form['length'],
                            request.form['gitcommit'],
                           )
            ).fetchall()
        
            if len(res) > 0:
                error = "This entry already in database. Created on %s" % ",".join(r['created'].strftime("%Y-%m-%d") for r in res)
        
        if error == None:
            #disable all other cranks
            db.execute('UPDATE Cranks SET Current = "FALSE" WHERE Current = "TRUE"')
            
            #insert new entry
            db.execute(
                'INSERT INTO Cranks (Crank,Stateset,Length,Gitcommit,Current)'
                'VALUES (?,?,?,?,?)',
                (request.form['crank'],
                 request.form['stateset'],
                 request.form['length'],
                 request.form['gitcommit'],                 
                 "TRUE")
            )
            db.commit()
                
            for key in ('crank','stateset','length','gitcommit','admincode'):
                session.pop(key,None)
                
            flash("Successfully added crank info")

    if error:
        flash(error)

    cranks = db.execute("SELECT * FROM Cranks ORDER by Created DESC").fetchall()        
    return render_template('admin.html',cranks=cranks,session=session)
