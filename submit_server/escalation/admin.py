DELIMITER = ','
BAD_DELIMITERS = set('\t, |.') - set(DELIMITER)  # common delimiters that are disallowed
import os

from flask import (
    Blueprint, flash, render_template, request, session, jsonify
)
from werkzeug.utils import secure_filename
from flask import current_app as app

from submit_server.escalation import database as db
from submit_server.escalation.dashboard import update_auto, update_science
from submit_server.escalation import scheduler, PERSISTENT_STORAGE, STATESETS_PATH, TRAINING_DATA_PATH


session_vars= ('githash','adminkey','username','crank')
# check that admin key is correct, git commit is 7 digits and csv file is the right format
def validate(adminkey,githash,filename):
    if adminkey != app.config['ADMIN_KEY']:
        return "Wrong admin key"
    
    if len(githash) != 7:
        return "Git commit hash is not 7 characters (current length is %d)" % len(githash)

    header=""
    #make sure file is comma  delimited
    with open(os.path.join(app.config[PERSISTENT_STORAGE], filename), 'r') as fh:
        for header in fh:
            if header[0] != '#':
                break

    required_header="dataset,name,_rxn_M_inorganic,_rxn_M_organic,_rxn_M_acid"
    if header.strip() != required_header:
        return "csv file does not have required header '%s'" % required_header
    
    return None

bp = Blueprint('admin',__name__)
@bp.route('/admin', methods=('GET','POST'))
def admin():
    error = None

    if request.method == 'POST' and request.headers.get('User-Agent') == 'escalation' and request.form['submit'] == 'training_run':    
        training = request.files['perovskitedata']
        training_file = os.path.join(app.config[PERSISTENT_STORAGE], secure_filename(training.filename))
                
        username = request.form['username']
        crank = request.form['crank']                
        githash  = request.form['githash']

        app.logger.info("Received request: {} {} {} {}".format(training_file,username,crank,githash))
        training.save(training_file)
        num_train_rows = db.add_training(training_file,githash,crank)
        
        out="Successfully added training run data for %s with %d rows" % (crank,num_train_rows)
        app.logger.info(out)

        # kick off stats refresh
        job1 = scheduler.add_job(func=update_science, args=[], id = 'update_science')
        job2 = scheduler.add_job(func=update_auto, args=[], id = 'update_auto')
        return jsonify({'success':'added training data for %s with %d rows' % (crank,num_train_rows)}), 200        

    if request.method == 'POST' and request.headers.get('User-Agent') == 'escalation' and request.form['submit'] == 'stateset':
        stateset = request.files['stateset']
        # note- this is a tmp filename because it is only a portion of the stateset, subsetted by the upload script
        stateset_filename = os.path.join(STATESETS_PATH, secure_filename(stateset.filename))

        training = request.files['perovskitedata']
        original_training_filename = training.filename
        training_filename = os.path.join(TRAINING_DATA_PATH, secure_filename(original_training_filename))
                
        username = request.form['username']
        crank = request.form['crank']                
        githash = request.form['githash']
        orig_filename = request.form['filename']
        app.logger.info("Received request: {} {} {} {} {}".format(stateset_filename, training_filename, username, crank, githash))

        if db.is_stateset_stored(crank,githash):
            error = 'Crank and githash already stored in database'
        else:
            stateset.save(os.path.join(app.config[PERSISTENT_STORAGE], stateset_filename))
            training.save(os.path.join(app.config[PERSISTENT_STORAGE], training_filename))
            error = validate(request.form['adminkey'], githash, stateset_filename)

        if error is None:
            num_train_rows = db.add_training(os.path.join(app.config[PERSISTENT_STORAGE], training_filename), githash, crank)
            num_rows = db.add_stateset(stateset_filename, crank, githash, username, orig_filename, training_filename, num_train_rows)

            out="Successfully updated to crank %s and stateset %s with %d rows" % (crank, githash,num_rows)
            app.logger.info(out)

            # kick off stats refresh
            job1 = scheduler.add_job(func=update_science, args=[], id = 'update_science')
            job2 = scheduler.add_job(func=update_auto, args=[], id = 'update_auto')
            return jsonify({'success':'updated to crank %s and commit hash %s with %d rows' % (crank,githash,num_rows)}), 200        
        else:
            app.logger.error(error)            
            return jsonify({'error':error}), 400

    if request.method == 'POST' and request.form['submit'] == "Update active cranks":
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:

            # check that only one entry per crank is active
            seen={}
            cranks = db.get_cranks()
            for crank in cranks:
                id = str(crank.id)
                if id in request.form and request.form[id] == 'active':
                    if crank.crank in seen:
                        flash("Can only have one active row for crank %s" % crank.crank)
                        cranks=[] #cute way to prevent updating any cranks below
                        break
                    seen[crank.crank] = 1

            # now update cranks (this will be empty if we break the logic)
            for crank in cranks:
                id = str(crank.id)
                if id not in request.form:
                    continue


                
                new_status = request.form[id] == 'active'
                if new_status != crank.active:
                    db.update_crank_status(crank.id,new_status)
                    out="Updating crank %s to %s" % (crank.crank,  'active' if new_status else 'inactive')
                    flash(out)
                    app.logger.info(out)
                    
    if request.method == 'POST' and request.form['submit'] == 'Update Database':
        for k in request.form:
            app.logger.info(k)
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:
            from .database import delete_db
            if request.form['db'] == 'reset':
                delete_db()
                app.logger.info("Deleted all data")
                flash("Deleted all data")
            else:
                flash("Unknown command, doing nothing")
            
    if request.method == 'POST' and  request.form['submit'] == "Update Chemical Names":
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            return jsonify({'error':'incorrect admin key'}),400

        id_arr     = request.form.getlist('id')
        inchi_arr  = request.form.getlist('inchi')
        name_arr   = request.form.getlist('common_name')
        abbrev_arr = request.form.getlist('abbrev')
        delete_arr = request.form.getlist('delete')
        
        if (len(abbrev_arr) != len(inchi_arr)) or (len(abbrev_arr) != len(name_arr)):
            app.logger.error("Missing a field somehow:inchi len=%d, name len=%d, abbrev len=%d" % (len(inchi_arr), len(name_arr),len(abbrev_arr)))                
            return jsonify({'error':"missing a field somehow:inchi len=%d, name len=%d, abbrev len=%d" % (len(inchi_arr), len(name_arr),len(abbrev_arr))}), 400
                
        for i, id in enumerate(id_arr):
            app.logger.info("Setting chemical %s %s %s" % (inchi_arr[i], name_arr[i], abbrev_arr[i]))
            if inchi_arr[i] == "" or name_arr[i] == "" or abbrev_arr[i] == "":
                app.logger.info("Skipping row %d due to blank value" % i)
            else:
                db.set_chemical(inchi_arr[i], name_arr[i], abbrev_arr[i])

        app.logger.info("Updated chemical set")                        
        return jsonify({'success':"Added %d chemicals" % len(inchi_arr)})
            
    return render_template('admin.html',cranks=db.get_cranks(),session=session,chem_table=db.get_chemicals())


