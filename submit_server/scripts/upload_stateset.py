import hashlib
import tempfile
import os
import git
import yaml
import requests
import pandas as pd
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="Rest endpoint",default='http://escalation.sd2e.org/admin')
parser.add_argument('--data',help="verisoned data path",default='../../versioned-datasets')
parser.add_argument('--key',help="admin secret key",default='secret')
args=parser.parse_args()

# compute md5 hash using small chunks
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_files_of_necessary_types(versioned_datasets_repo_path):
    # get information from the perovskite manifest for the template
    perovskite_manifest_filename = 'perovskite.manifest.yml'

    try:
        with open(os.path.join(versioned_datasets_repo_path, 'manifest', perovskite_manifest_filename)) as mf:
            perovskite_manifest = yaml.load(mf)
    except FileNotFoundError:
        print("!!\n!!\n!! Unable to find perovskites manifest.  Try changing the versioned-datasets repo path in local_versioned_data_repo_path.py or deleting the file to resolve.\n")
        raise

    # the perovskite manifest should only have one each uncommented file of training data and stateset at a same time
    file_names = perovskite_manifest['files']

    file_types = {
        'perovskitedata': None,
        'stateset': None,
    }

    for file_name in file_names:
        # file_name_components = file_name.split('/')
        # assert(len(file_name_components) == 2, 'A file with an unrecognized name format is in the manifest')
        base_filename = os.path.basename(file_name)
        versioned_file_type = base_filename.split('.')[-2]
        if versioned_file_type in file_types and not file_types.get(versioned_file_type):
            file_types[versioned_file_type] = file_name

    for file_type, file_name in file_types.items():
        if file_name is None:
            raise ValueError("Unable to find a file in the perovskites manifest of type: %s" % file_type)
    return file_types
    
def get_git_info(versioned_datasets_repo_path):
    # get information from the git repo about the user and the current commit
    repo = git.Repo(versioned_datasets_repo_path)
    git_sha = repo.head.object.hexsha
    reader = repo.config_reader()

    try:
        git_username = reader.get_value("user", "name")
    except NoOptionError:
        print("User name is not defined. Run 'git config --global user.name <uname>'")
        exit(1)
        
    return git_sha, git_username

git_sha, git_username = get_git_info(args.data)
files = get_files_of_necessary_types(args.data)

csvfile=tempfile.mkstemp()[1]
stateset = os.path.join(args.data,'data','perovskite',files['stateset'])
crank = os.path.basename(files['perovskitedata']).split('.')[0]
print("Filtering",stateset,"to",csvfile)

#TODO: turn into a file and reduce I/O
df = pd.read_csv(stateset,comment='#')
df = df[['dataset','name','_rxn_M_inorganic','_rxn_M_organic']]
df['dataset'] = md5(stateset)[:11]
df.to_csv(csvfile,index=False)

#TODO:manipulate stateset
print("Pushing filtered csv to",args.endpoint)

r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},data={'crank':crank,'githash':git_sha[:7], 'username':git_username,'adminkey':args.key},
                  files={'csvfile':open(csvfile,'rb')},timeout=600)
print(r.status_code, r.reason,r)
try:
    print(r.json())
except:
    pass
