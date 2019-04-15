import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="REST endpoint",default='http://escalation.sd2e.org/features')
parser.add_argument('--json',help="json file. See 'feature_importance_sample.json'")
parser.add_argument('--githash',help="7 digit git commit of versioned data repo")
args=parser.parse_args()
if args.json is None:
    print("Must pass in json")
    exit()
    
if args.githash is None or len(args.githash) != 7:
    print("Must pass in 7 digit hash of your versioned-data repo head")
    exit()

obj = json.load(open(args.json))

err=False
for form in ('method','crank','notes','chem_heldout','all_chem','features'):
    if form not in obj:
        print("Must include",form," in form")
        err=True

for x in ('chem_heldout','all_chem'):
    for f in obj[x]:
        if type(obj[x][f]) != list:
            print(x,f,"is not a list")
            if len(obj[x][f][0]) < 3:
                print(x,f,"does not have 3+ samples")
            if len(obj[x][f][1]) < 3:
                print(x,f,"does not have 3+ samples")
            if len(obj[x][f][1] != obj[x][f][0]):
                print (x,f,"does not have equal length ranks and values")
                
if err:
    exit()
    
r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},json=obj, timeout = 60)
print(r.status_code, r.reason,r)
try:
    print(r.json())
except:
    pass
    
