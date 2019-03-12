# Here is a list of possible validations on the submission template:
# 1. I really like the structural validations, all of the ones that you suggested should be present
# 2. Strict enforcement of the 11 character md5 hash of the stateset, and having a value in each of the subsequent columns for each entry
# 3. Ensure that the values of name, _rxn_M_inorganic, and _rxn_M_organic, all correspond to the appropriate row in the state set
# 3 a. Based on the name of the row (0,1,2,3,etc) the _rxn_M* columns should be identical to those in the state set (the state set with the same crank number)

import csv
DELIMITER = ','
VALID_CATEGORIES = set([1,2,3,4])
BAD_DELIMITERS = set('\t, |.') - set(DELIMITER)  # common delimiters that are disallowed
COLUMNS = ['dataset','name','_rxn_M_inorganic','_rxn_M_organic','predicted_out','score']

from flask import current_app as app
from . import database as db

def isclose(a,b,rtol=1e-05,atol=1e-08):
        return abs(a - b) <= (atol + rtol * abs(b))
        
def validate_submission(contents,stateset=None):
    arr = []
    contents = contents.split("\n")
    app.logger.debug("Reading %d lines starting with %s" % (len(contents), contents[0]))

    if len(contents) == 1:
        return ["Submission file appears empty"]

    for line in contents:
        if len(line)==0:
                continue
        if line[0] != '#':
            break

    if any(d in line.split(DELIMITER)[0] for d in BAD_DELIMITERS):
        arr.append("file does not appear to be comma delimited. No tabs or spaces allowed")
        return arr
    cols = line.strip().split(DELIMITER)

    if len(cols) != len(COLUMNS):
        arr.append(",".join(cols) + "Extra columns in uploaded CSV.<br/> expected: '%s'" % " , ".join(COLUMNS))
        return arr
    
    for i, col in enumerate(cols):
         if COLUMNS[i] != col:
            arr.append( "Wrong columns uploaded.<br/>Received '%s'<br/>expected '%s'" % (",".join(cols), ",".join(COLUMNS)))
            return arr

    rows=[]
    reader = csv.DictReader(filter(lambda row:row[0] != '#', contents))
    #FIXME: could this be sped up?

    for row in reader:
        stateset=row['dataset'] #FIXME: will need to remove and pass in stateset as top level param
        rows.append(row)

    names = [r['name'] for r in rows]
    rxns = db.get_rxns(stateset,names)
            
    # validate each row
    num_errors = 0
    if len(rxns) != len(rows):
        app.logger.info("Only found %d of %d submitted rows in current stateset -- maybe there is a typo in the dataset or name field?" % (len(rxns),len(rows)))
        arr.append("Only found %d of %d submitted rows in current stateset -- maybe there is a typo in the dataset or name field?" % (len(rxns),len(rows)))
        return arr
    
    for i, row in enumerate(rows):

        if num_errors > 10:
            arr.append("Stopping checks due to more than 10 errors")
            break

        if None in row.values():
            num_errors+=1
            arr.append("Row %d does not contain the right number of values" %i)
            app.logger.debug("Skipping row %d" % i)
            continue
    
        if stateset and row['dataset'] != stateset:
            num_errors+=1
            arr.append("Row %d 'dataset' column (%s) is not 11 chars. Is it the state set hash?" % (i, row['dataset']))
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

        organic, inorganic = rxns[row['name']]['organic'], rxns[row['name']]['inorganic']
        
        if not (isclose(float(row['_rxn_M_inorganic']),float(inorganic),1e-03,1e-05)):
            num_errors += 1
            arr.append("Row %d '_rxn_M_inorganic' value %s does not match statespace value '%s' -- did you mix up rows?" % (i,row['_rxn_M_inorganic'],inorganic))

        if not (isclose(float(row['_rxn_M_organic']),float(organic),1e-03,1e-05)):
            num_errors += 1
            arr.append("Row %d '_rxn_M_organic' value %s does not match statespace value '%s' -- did you mix up rows?" % (i,row['_rxn_M_organic'],organic))

    print(arr)
    if len(arr) > 0:
        return arr
    else:
        return None

if __name__ == '__main__':
    import sys
    print(validate_submission(sys.argv[1]))
