# Manually uploading a submission

## One time: Install dependencies

Setup versioned data repo to have access to the files. https://gitlab.sd2e.org/sd2program/versioned-datasets/

## Download latest perovskite crank data

1. `cd` to your `versioned-data` directory
2. Get the latest perovskites list of files (manifest) with `git pull origin master`
3. Download the latest files with `python3 scripts/pull_data.py manifest/perovskite.manifest.yml`

## Create a blank submission csv

On first run, the script asks for the path to the local install of this repo, which it caches in a file.
It uses the repo path to get information about the current git version of the versioned data code.

Run `python make_perovskites_blank_submission.py`, to produce a `.csv` formatted with the correct file name and column structure.

The Format of the file is a CSV, comma separated

Column names:

`dataset,name,_rxn_M_inorganic,_rxn_M_organic,_rxn_M_acid,predicted_out,score`

The first five columns can be directly taken from the `stateset` file. They are present for data validation to help make sure you are uploading the right data format.

Column data schema:
| Column Name     | Data Type  |
|-----------------|------------|
| dataset         | Crank number `type=str`   |
| name            | crank/run # `type=int` |
| rxn_M_inorganic | truncated 5 decimal places `type=float` |
| rxn_M_organic   | truncated 5 decimal places `type=float`  |
| rxn_M_acid      | truncated 5 decimal places `type=float`  |
| predicted_out   |  1-4 `type=int` |
| score           |  0-1 (confidence) `type=float` |


## Upload submission.

Either visit http://escalation.sd2e.org/submission

Or use the upload script that will parse the previously created CSV

```
python3 submit_server/scripts/upload_submission.py --csv 0019_train_3c89514_snovotney.csv --notes "these are my additional notes" 
```
