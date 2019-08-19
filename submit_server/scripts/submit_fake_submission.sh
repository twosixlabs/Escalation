
python3 scripts/upload_submission.py --csv tests/0001_file1.csv  --user snovot --expname first --crank 0001 --notes "these are my notes" --endpoint http://127.0.0.1:5000/submission --dev
python3 scripts/upload_submission.py --csv tests/0001_file2.csv  --user snovot --expname second --crank 0001 --notes "don't you like my notes" --endpoint http://127.0.0.1:5000/submission --dev
python3 scripts/upload_submission.py --csv tests/0001_file3.csv  --user snovot --expname third --crank 0001 --notes "really cool notes" --endpoint http://127.0.0.1:5000/submission --dev

# set to 0002
python3 scripts/upload_stateset.py --debug

python3 scripts/upload_submission.py --csv tests/0002_file1.csv  --user snovot --expname first --crank 0002 --notes "these are my notes" --endpoint http://127.0.0.1:5000/submission --dev
python3 scripts/upload_submission.py --csv tests/0002_file2.csv  --user snovot --expname second --crank 0002 --notes "don't you like my notes" --endpoint http://127.0.0.1:5000/submission --dev
