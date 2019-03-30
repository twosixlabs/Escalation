import traceback
from flask import current_app as app
from . import database as db

import shutil
from tempfile import mkdtemp
import os
import io
import time
import csv

DELIMITER = ','
VALID_CATEGORIES = set([1,2,3,4])
BAD_DELIMITERS = set('\t, |.') - set(DELIMITER)  # common delimiters that are disallowed
COLUMNS = ['dataset','name','_rxn_M_inorganic','_rxn_M_organic','_rxn_M_acid','predicted_out','score']

def filename(sub):
    #id, crank, username, expname
    return "%05d_%s_%s_%s.csv" %(sub.id,sub.crank,sub.username.replace(' ','-'),sub.expname.replace(' ','-'))

def isclose(a,b,rtol=1e-05,atol=1e-08):
        return abs(a - b) <= (atol + rtol * abs(b))

def text2rows(text):
    reader = csv.DictReader(filter(lambda row: row[0]!='#', io.StringIO(text)))
    data = list(reader)
    comments=[]
    for l in text.split("\n"):
        if '#' in l:
            comments.append(l)
        else:
            break

    app.logger.info("Extracted %d lines of data and %d comments" % (len(data), len(comments)))            

    if len(comments) > 0:
        comments = "\n".join(comments)
    else:
        comments = None

    return data, comments
    
def validate_submission(rows,crank,githash):
    arr = []
    app.logger.info("Validating %d lines" % len(rows))

    if len(rows) == 0:
        return ["Submission file appears empty"]

    try:
        names = [r['name'] for r in rows]
        rxns = db.get_rxns(crank,githash,names)
        # validate each row
        if len(rxns) != len(rows):
            app.logger.info("Only found %d of %d submitted rows in current stateset -- maybe there is a typo in the dataset or name field?" % (len(rxns),len(rows)))
            arr.append("Only found %d of %d submitted rows in current stateset -- maybe there is a typo in the dataset or name field?" % (len(rxns),len(rows)))
            return arr
    except:
        return ["Could not extract 'name' column from rows"]

    num_errors = 0
    for i, row in enumerate(rows):
        if num_errors > 10:
            arr.append("Stopping checks due to more than 10 errors")
            break

        if len(row.keys()) != len(COLUMNS):
               arr.append("Row %d: Number of columns (%d) does not match expected number of %d. Maybe you are missing a comma in this row or the header?" % len(row.keys()), len(COLUMNS))
               continue
        if set (row.keys()) != set(COLUMNS):
            num_errors+=1
            not_found = []
            for key in row.keys():
                if key not in COLUMNS and key is not None:
                    print(key)
                    not_found.append(key)
            arr.append("Row %d: columns '%s' not in expected set of columns: '%s'" % (i,",".join(not_found),",".join(COLUMNS)))
            continue
        
        if None in row.values() or '' in row.values():
            num_errors+=1
            arr.append("Row %d does not contain the right number of values" %i)
            app.logger.debug("Skipping row %d" % i)
            continue
    
        if row['dataset'] != crank:
            num_errors+=1
            arr.append("Row %d 'dataset' column (%s) does not match expected crank '%s' ?" % (i, row['dataset'],crank))
        try:
            int(row['name'])
        except ValueError:
            num_errors+=1                
            arr.append("Row %d 'name' column (%s) is not an int. Is it the run number?" % (i, row['name']))                            
        try:
            float(row['_rxn_M_inorganic'])
        except ValueError:
            num_errors+=1                
            arr.append("Row %d '_rxn_M_inorganic' column (%s) is not a float. Did you use the values from the state set?" % (i, row['_rxn_M_inorganic']))                            
        try:
            float(row['_rxn_M_organic'])
        except ValueError:
            num_errors+=1                
            arr.append("Row %d '_rxn_M_organic' column (%s) is not a float. Did you use the values from the state set?" % (i, row['_rxn_M_organic']))
        try:
            float(row['_rxn_M_acid'])
        except ValueError:
            num_errors+=1                
            arr.append("Row %d '_rxn_M_acid' column (%s) is not a float. Did you use the values from the state set?" % (i, row['_rxn_M_acid']))                            
            
        try:
            if int(row['predicted_out']) not in VALID_CATEGORIES:
                num_errors+=1
                arr.append("Row %d 'predicted_out' column (%s) is not in %s" %(i,row['predicted_out'],",".join([str(x) for x in VALID_CATEGORIES])))
        except ValueError:
            num_errors+=1                
            arr.append("Row %d 'predicted_out' column (%s) is not an int. Did you use the values from the state set?" % (i, row['predicted_out']))            
        try:
            x=float(row['score'])
            if x < 0 or x > 1:
                num_errors+=1
                arr.append("Row %d 'score' column (%s) is not a float within [0,1]" % (i,row['score']))
        except ValueError:
            num_errors+=1                
            arr.append("Row %d 'score' column (%s) is not a float. Did you use the values from the state set?" % (i, row['score']))                        

        organic   = rxns[row['name']]['organic']
        inorganic = rxns[row['name']]['inorganic']
        acid      = rxns[row['name']]['acid']
        
        if not (isclose(float(row['_rxn_M_inorganic']),float(inorganic),1e-03,1e-05)):
            num_errors += 1
            arr.append("Row %d '_rxn_M_inorganic' value %s does not match statespace value '%s' -- did you mix up rows?" % (i,row['_rxn_M_inorganic'],inorganic))

        if not (isclose(float(row['_rxn_M_organic']),float(organic),1e-03,1e-05)):
            num_errors += 1
            arr.append("Row %d '_rxn_M_organic' value %s does not match statespace value '%s' -- did you mix up rows?" % (i,row['_rxn_M_organic'],organic))

        if not (isclose(float(row['_rxn_M_acid']),float(acid),1e-03,1e-05)):
            num_errors += 1
            arr.append("Row %d '_rxn_M_acid' value %s does not match statespace value '%s' -- did you mix up rows?" % (i,row['_rxn_M_acid'],acid))

    if len(arr) > 0:
        return arr
    else:
        return None

def download_zip(basedir,submissions,pfx=""):
    tmpdir = mkdtemp()
    metadata=[]
    for sub in submissions:
        fname = filename(sub)
        metadata.append({'user':sub.username,
                         'id': sub.id,
                         'crank':sub.crank,
                         'created':sub.created,
                         'expname':sub.expname,
                         'notes':sub.notes,
                         'filename':fname,
        })
        
    with open(os.path.join(tmpdir,'metadata.csv'),'w') as csvfile:
        fieldnames = ['id','user','crank','created','expname','filename']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n',extrasaction='ignore')
        writer.writeheader()
        for elem in metadata:
            writer.writerow(elem)

    for sub in submissions:
        preds = [p.__dict__ for p in sub.rows] #map to dict for csv.dictwriter
        app.logger.info("Writing %d predictions for %s" % (len(preds), sub))
        fname = filename(sub)
        fh =  open(os.path.join(tmpdir,fname),'w')
        fh.write("# " + sub.notes.replace("\n","\n# ") + "\n")
        writer = csv.DictWriter(fh, fieldnames=['dataset','name','predicted_out','score'],extrasaction='ignore',lineterminator='\n')
        writer.writeheader()
        for row in preds:
            writer.writerow(row)
        fh.close()
            
    if pfx:
        curr = "escalation." + str(pfx) + "." + time.strftime("%Y%m%d-%H%M%S",time.localtime())
    else:
        curr = "escalation." + time.strftime("%Y-%m-%d-%H%M%S",time.localtime())
        
        
    shutil.make_archive(os.path.join(basedir,curr),'zip',tmpdir)
    shutil.rmtree(tmpdir)

    return os.path.join(basedir,curr+".zip")
