"""
This script creates a blank submission template.
It relies on the user having installed the versioned datasets code, and providing a path that repo installed locally.
The path to the versioned datasets repo is cached in local_versioned_data_repo_path.py
"""

import git
import os
import yaml

# handles python 2/3 compatibility
from builtins import input


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
    git_username = reader.get_value("user", "name")
    return git_sha, git_username


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


def get_submission_template_info():
    versioned_datasets_repo_path = get_versioned_data_repo_directory()
    print("Using {} as versioned-datasets path.  Getting git commit from data there.".format(
        versioned_datasets_repo_path))
    file_types = get_files_of_necessary_types(versioned_datasets_repo_path)
    git_sha, git_username = get_git_info(versioned_datasets_repo_path)
    training_data_git_hash = git_sha[:7]
    # NB: they could have checked this code out without pulling the most recent dataset using the pull script,
    # but that should be caught by having a stale crank number
    print("Git commit of local versioned-datasets manifest: {}.  Git username: {}".format(git_sha, git_username))
    # file name formatted like 0015.trainingdata.csv
    crank_number = os.path.basename(file_types['perovskitedata']).split('.')[0]
    git_username_no_whitespace = git_username.replace(' ', '')
    submission_template_filename = '_'.join([crank_number,
                                             'train',
                                             training_data_git_hash,
                                             git_username_no_whitespace]) + '.csv'
    return submission_template_filename, git_username


def make_submission_template_csv():
    submission_template_filename, git_username = get_submission_template_info()
    # Create a submission template file in the locatin that the script was run
    with open(submission_template_filename, 'w') as fout:
        fout.write("# USERNAME: %s\n" % git_username)
        fout.write("# USER CAN ENTER COMMENT LINES WITH MODEL USED OR NOTES HERE\n")
        fout.write(
            "# Data schema: <11 character hash of state type=str>, <run# type=int>, <truncated 5 decimal places type=float>,<truncated 5 decimal places type=float>, <1-4 type=int>, <0-1 (confidence) type=float\n")
        fout.write("dataset,name,_rxn_M_inorganic,_rxn_M_organic,predicted_out,score\n")

    print("Created file %s" % submission_template_filename)


if __name__ == '__main__':
    make_submission_template_csv()