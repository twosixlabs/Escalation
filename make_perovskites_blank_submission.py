"""
This script creates a blank submission template.
It relies on the user having installed the versioned datasets code, and providing a path that repo installed locally.
The path to the versioned datasets repo is cached in local_versioned_data_repo_path.py
"""

import os
from configparser import NoOptionError
import argparse
# handles python 2/3 compatibility
from builtins import input

parser = argparse.ArgumentParser()
parser.add_argument('--debug',help="Use debug manifest and dev endpoint",action='store_true')
args=parser.parse_args()

import utils


def get_submission_template_info():
    versioned_datasets_repo_path = utils.get_versioned_data_repo_directory()
    print("Using {} as versioned-datasets path.  Getting git commit from data there.".format(
        versioned_datasets_repo_path))
    file_types = utils.get_files_of_necessary_types(versioned_datasets_repo_path,args.debug)
    git_sha, git_username = utils.get_git_info(versioned_datasets_repo_path)
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
            "# Data schema: <11 character md5 hash of state type=str>, <run# type=int>, <truncated 5 decimal places type=float>,<truncated 5 decimal places type=float>,<truncated 5 decimal places type=float>, <1-4 type=int>, <0-1 (confidence) type=float\n")
        fout.write("dataset,name,_rxn_M_inorganic,_rxn_M_organic,_rxn_M_acid,predicted_out,score\n")

    print("Created file %s" % submission_template_filename)


if __name__ == '__main__':
    make_submission_template_csv()
