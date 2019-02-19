### Create a blank submission csv

This relies on you also having the versioned-datasets repo installed (see Gitlab). 
On first run, the script asks for the path to the local install of this repo, which it caches in a file.
It uses the repo path to get information about the current git version of the versioned data code.

Run `python make_perovskites_blank_submission.py`, to produce a `.csv` formatted with the correct file name and column structure.

TODO: What info should be filled into the file by a user?