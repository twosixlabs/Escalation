### Create a blank submission csv

This relies on you also having the versioned-datasets repo installed (see Gitlab). 
On first run, the script asks for the path to the local install of this repo, which it caches in a file.
It uses the repo path to get information about the current git version of the versioned data code.

Run `python make_perovskites_blank_submission.py`, to produce a `.csv` formatted with the correct file name and column structure.

TODO: What info should be filled into the file by a user?


### Submission CSV Format

CSV, comma separated

Column names:

`dataset,name,_rxn_M_inorganic,_rxn_M_organic,predicted_out,score`

Column data schema:

| Column Name   | Data Type  |
|---------------|---|
| dataset       | 11 character md5 hash of state `type=str`   |
|    name           |  crank/run # `type=int` |
|     rxn_M_inorganic          |  truncated 5 decimal places `type=float` |
|     rxn_M_organic          | truncated 5 decimal places `type=float`  |
|    predicted_out           |  1-4 `type=int` |
|      score         |  0-1 (confidence) `type=float` |


