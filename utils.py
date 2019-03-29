import git
import os
import yaml
import re
from collections import defaultdict

def make_versioned_data_repo_path():
    user_input = input("Enter the absolute path of your versioned-datsets repo (e.g., /Users/nick.leiby/versioned-datasets/): ")
    assert os.path.exists(user_input), "Unable to find a versioned repo directory at:  "+str(user_input)
    with open('local_versioned_data_repo_path.py', 'w') as fout:
        fout.write("# This file acts as a local cache to the user's versioned dataset code\n")
        fout.write("repo_path = '%s'\n" % user_input)
    # import the repo_path from the python file cache we just created
    from local_versioned_data_repo_path import repo_path
    return repo_path


def get_versioned_data_repo_directory():
    try:
        from local_versioned_data_repo_path import repo_path
    except ModuleNotFoundError:
        repo_path = make_versioned_data_repo_path()
    return repo_path



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


def get_files_of_necessary_types(versioned_datasets_repo_path,debug=False):

    # get information from the perovskite manifest for the template
    perovskite_manifest_filename = 'perovskite.manifest.yml'
    if debug:
        print("Using debug.manifest.yml")
        perovskite_manifest_filename = 'debug.manifest.yml'
    try:
        with open(os.path.join(versioned_datasets_repo_path, 'manifest', perovskite_manifest_filename)) as mf:
            perovskite_manifest = yaml.load(mf)
    except FileNotFoundError:
        print("!!\n!!\n!! Unable to find perovskites manifest.  Try changing the versioned-datasets repo path in local_versioned_data_repo_path.py or deleting the file to resolve.\n")
        raise

    file_names = perovskite_manifest['files']

    file_types = ['perovskitedata','stateset']
    found_files = defaultdict(lambda: defaultdict(str))
    for file_name in file_names:
        # file_name_components = file_name.split('/')
        # assert(len(file_name_components) == 2, 'A file with an unrecognized name format is in the manifest')
        base_filename = os.path.basename(file_name)
        versioned_file_type = base_filename.split('.')[-2]
        crank  = re.findall(r'(\d{4})\.', base_filename)[0]

        if versioned_file_type in file_types:
            found_files[crank][versioned_file_type] = os.path.join(versioned_datasets_repo_path,'data',perovskite_manifest['project name'],file_name)


    for crank in found_files:
        for ft in file_types:
            if found_files[crank][ft] is None:
                raise Exception("Could not find %s for crank %s" %(ft, crank))
    return found_files


