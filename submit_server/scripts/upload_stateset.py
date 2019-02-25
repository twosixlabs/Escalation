import tempfile
import sys
import os
import git
import yaml
import requests
import pandas as pd

ADMIN_KEY='secret'
ENDPOINT = 'http://127.0.0.1:5000/admin'

#TODO: replace with opt
if len(sys.argv) > 2:
    ADMIN_KEY = sys.argv[2]
if len(sys.argv) > 3:
    ENDPOINT = sys.argv[3]
    
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

git_sha, git_username = get_git_info(sys.argv[1])
files = get_files_of_necessary_types(sys.argv[1])

csvfile=tempfile.mkstemp()[1]
stateset = os.path.join(sys.argv[1],'data','perovskite',files['stateset'])
print("Filtering",stateset,"to",csvfile)

#TODO: turn into a file and reduce I/O
df = pd.read_csv(stateset,comment='#')
df[['dataset','name','_rxn_M_inorganic','_rxn_M_organic']].to_csv(csvfile,index=False)

#TODO:manipulate stateset
print("Pushing filtered csv to",ENDPOINT)
r = requests.post(ENDPOINT, headers={'User-Agent':'escalation'},data={'user':git_username,'githash':git_sha[:7], 'adminkey':ADMIN_KEY},files={'csvfile':open(csvfile,'rb')})
print(r.status_code, r.reason,r)
print(r.json())
