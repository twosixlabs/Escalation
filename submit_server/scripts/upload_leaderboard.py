import requests
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="REST endpoint",default='http://escalation.sd2e.org/leaderboard')
parser.add_argument('--csv',help="csv file")
parser.add_argument('--gitcommit',help="7 digit git commit of versioned data repo")
args=parser.parse_args()

def mapping(name):
    return name.lower().replace(' ','_')
if args.csv is None:
    print("Must pass in csv")
    exit()
if args.gitcommit is None or len(args.gitcommit) != 7:
    print("Must pass in 7 digit gitcommit hash")
    exit()
fh = open(args.csv)
csvreader = csv.DictReader(filter(lambda row: row[0]!='#', fh))

for row in csvreader:
    d = {}
    d['gitcommit'] = args.gitcommit
    for k in row:
        d[k.lower().replace(' ','_')] = row[k]
        
    r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},data=d, timeout = 60)
    print(r.status_code, r.reason,r)
    try:
        print(r.json())
    except:
        pass
    
