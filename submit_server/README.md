# Build and push
```
VERSION=0.2
./build.sh
docker tag escalation-server:latest snovotney/escalation:$VERSION
docker push snovotney/escalation:$VERSION
```
# Run locally
` docker run --name escalation  -p 8000:5000 --rm -e SECRET_KEY=perovskites escalation-server:$VERSION`

Then go to `127.0.0.1:8000` in your brower


# Upload submissions outputted from `make_perovskites_blank_submission.py`
# Run `upload_submission.py --help` for custom options
`python3 submit_server/scripts/upload_submission.py --csv submit_server/tests/0017_train_c4844e9_snovotney.csv --expname first --notes "These are my awesome notes"`

# Update stateset to checked in stateset from versioned repo
# Run `upload_stateset.py --help` for custom options
`python3 submit_server/scripts/upload_stateset.py  --data ../versioned-datasets/`

Here's example output of running both
```
ython3 submit_server/scripts/upload_stateset.py  --data ../versioned-datasets/
Filtering ../versioned-datasets/data/perovskite/stateset/0017.stateset.csv to /var/folders/08/cb19qzd92wsbhh3n4cz145v00000gp/T/tmpbx31mcn6
Pushing filtered csv to http://escalation.sd2e.org/admin
200 OK <Response [200]>
{'success': 'updated to crank 0017 and stateset hash a301494d902 with 465426 rows'}
(venv) scott.novotney@mac0561:~/trunk/sd2/escalation$ python3 submit_server/scripts/upload_submission.py --csv submit_server/tests/0017_train_c4844e9_snovotney.csv --expname first
0017 c4844e9 snovotney
crank 0017
username snovotney
expname first
notes
csv submit_server/tests/0017_train_c4844e9_snovotney.csv
200 OK <Response [200]>
{'success': 'Added submission'}
```
