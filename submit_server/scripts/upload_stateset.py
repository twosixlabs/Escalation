import hashlib
import tempfile
import os
import git
import yaml
import requests
import pandas as pd
import argparse
import sys

#don't judge me -- cute way to import the utils module from two dirs up
base=os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(base,'../../'))
import utils
                
parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="Rest endpoint",default='http://escalation.sd2e.org/admin')
parser.add_argument('--debug',help="Use debug manifest and dev endpoint",action='store_true')
parser.add_argument('--key',help="admin secret key",default='secret')
args=parser.parse_args()

if args.debug and args.endpoint == 'http://escalation.sd2e.org/admin':
    args.endpoint = 'http://127.0.0.1:5000/admin'

print("POSTing to",args.endpoint)    
# compute md5 hash using small chunks
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


versioned_datasets_repo_path = utils.get_versioned_data_repo_directory()
git_sha, git_username = utils.get_git_info(versioned_datasets_repo_path)
files = utils.get_files_of_necessary_types(versioned_datasets_repo_path,args.debug)

#TODO: check if manifest is clean or dirty!


# very hardcoded pths
stateset       = os.path.join(versioned_datasets_repo_path,'data','perovskite',files['stateset'])
perovskitedata = os.path.join(versioned_datasets_repo_path,'data','perovskite',files['perovskitedata'])
crank = os.path.basename(files['perovskitedata']).split('.')[0]

stateset_csv=tempfile.mkstemp()[1]
print("Filtering",stateset,"to",stateset_csv)

#TODO: turn into a file and reduce I/O
df = pd.read_csv(stateset,comment='#')
df = df[['dataset','name','_rxn_M_inorganic','_rxn_M_organic']]
df['dataset'] = md5(stateset)[:11]
df.to_csv(stateset_csv,index=False)

perovskite_csv=tempfile.mkstemp()[1]
print("Filtering",perovskitedata,"to",perovskite_csv)

#TODO: turn into a file and reduce I/O
df2 = pd.read_csv(perovskitedata,comment='#',dtype={'dataset': 'str'})
df2 = df2[['dataset','name','_out_crystalscore','_rxn_M_acid','_rxn_M_inorganic','_rxn_M_organic','_rxn_organic-inchikey']]
orig_len = len(df2)
df2 = df2[~df2._out_crystalscore.isna()]
if len(df2) != orig_len:
    print("WARNIING: Removed %d NA values from perovskitesdata before uploading" % (orig_len  - len(df2)))
df2._out_crystalscore = df2._out_crystalscore.astype(int)
df2.to_csv(perovskite_csv,index=False)

print("Pushing %d rows from %s and %d rows from %s to %s . Could take a minute or two." % (len(df),stateset_csv, len(df2),perovskite_csv,args.endpoint))

r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},data={'crank':crank,'githash':git_sha[:7], 'username':git_username,'adminkey':args.key},
                  files={'stateset':open(stateset_csv,'rb'), 'perovskitedata':open(perovskite_csv,'rb')},timeout=300)
print(r.status_code, r.reason,r)
try:
    print(r.json())
except:
    pass
