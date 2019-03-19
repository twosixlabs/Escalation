import git
import os
import yaml

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
            file_types[versioned_file_type] = os.path.join(versioned_datasets_repo_path,'data',perovskite_manifest['project name'],file_name)

    for file_type, file_name in file_types.items():
        if file_name is None:
            raise ValueError("Unable to find a file in the perovskites manifest of type: %s" % file_type)
    return file_types


