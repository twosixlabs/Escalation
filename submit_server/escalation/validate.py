
# Here is a list of possible validations on the submission template:
# 1. I really like the structural validations, all of the ones that you suggested should be present
# 2. Strict enforcement of the 11 character md5 hash of the stateset, and having a value in each of the subsequent columns for each entry
# 3. Ensure that the values of name, _rxn_M_inorganic, and _rxn_M_organic, all correspond to the appropriate row in the state set
# 3 a. Based on the name of the row (0,1,2,3,etc) the _rxn_M* columns should be identical to those in the state set (the state set with the same crank number)

import pandas as pd
DELIMITER = ','
BAD_DELIMITERS = set('\t, |.') - set(DELIMITER)  # common delimiters that are disallowed
COLUMNS = ['dataset','name,_rxn_M_inorganic','_rxn_M_organic','predicted_out','score']

def arr2html(arr):
    out="<ul>\n"
    out += "\n".join("<li>%s</li>" % x for x in arr)
    out += "\n</ul>\n"
    return out

def validate_submission(f):
    
    arr = []

    #make sure file is comma  delimited
    with open(f, 'r') as fh:
        for header in fh:
            if header[0] != '#':
                break
    if any(d in header.split(DELIMITER)[0] for d in BAD_DELIMITERS):
        arr.append("file does not appear to be comma delimited. Expecting only ',', not tabs or spaces")

    #make sure columns match
    for chunk in pd.read_csv(f, chunksize=10, sep=DELIMITER, comment='#', low_memory=False):
        cols = chunk.columns
        for i, col in enumerate(cols):
            if COLUMNS[i] != col:
                arr.append( "Wrong columns uploaded.<br/>Received '%s'<br/>expected '%s'" % (",".join(cols), ",".join(COLUMNS)))
                break
        break

    if len(arr) > 0:
        return arr2html(arr)
    else:
        return None

if __name__ == '__main__':
    import sys
    print(validate_submission(sys.argv[1]))
