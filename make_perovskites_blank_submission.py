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
    files = utils.get_files_of_necessary_types(versioned_datasets_repo_path,args.debug)
    git_sha, git_username = utils.get_git_info(versioned_datasets_repo_path)
    training_data_git_hash = git_sha[:7]

    print("Git commit of local versioned-datasets manifest: {}.  Git username: {}".format(git_sha, git_username))
    # file name formatted like 0015.trainingdata.csv

    git_username_no_whitespace = git_username.replace(' ', '')
    for crank_number in files:    
        submission_template_filename = '_'.join([crank_number,
                                                 'train',
                                                 training_data_git_hash,
                                                 git_username_no_whitespace]) + '.csv'

        # Create a submission template file in the location that the script was run
        with open(submission_template_filename, 'w') as fout:
            fout.write("# USERNAME: %s\n" % git_username)
            fout.write("# USER CAN ENTER COMMENT LINES WITH MODEL USED OR NOTES HERE\n")
            fout.write(
                "# Data schema: <11 character md5 hash of state type=str>, <run# type=int>, <truncated 5 decimal places type=float>,<truncated 5 decimal places type=float>,<truncated 5 decimal places type=float>, <1-4 type=int>, <0-1 (confidence) type=float\n")
            fout.write("dataset,name,_rxn_M_inorganic,_rxn_M_organic,_rxn_M_acid,predicted_out,score\n")
            print("Created file %s" % submission_template_filename)


if __name__ == '__main__':
    get_submission_template_info()
