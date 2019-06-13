import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="REST endpoint",default='http://escalation.sd2e.org/features')
parser.add_argument('--dev',help="Use dev manifest and dev endpoint",action='store_true')
parser.add_argument('--json',help="json file. See 'feature_importance_sample.json'")
parser.add_argument('--githash',help="7 digit git commit of versioned data repo")
args=parser.parse_args()


if args.dev and args.endpoint == 'http://escalation.sd2e.org/features':
    args.endpoint = 'http://escalation-dev.sd2e.org/features'
    
print("Uploading to",args.endpoint)

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

err=False
for x in ('chem_heldout','all_chem'):
    for f in obj[x]:
        if 'value' not in obj[x][f]:
            print(x,f,"'value' not present")
            err=True
        elif 'rank' not in obj[x][f]:
            print(x,f,"'value' not present")
            err=True            
        elif len(obj[x][f]['value']) < 3:
            print(x,f,"does not have 3+ samples")
            err=True            
        elif len(obj[x][f]['rank']) < 3:
            print(x,f,"does not have 3+ samples")
            err=True            
        elif len(obj[x][f]['value']) != len(obj[x][f]['rank']):
            print (x,f,"does not have equal length ranks and values")
            err=True            
                
if err:
    exit()
    
r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},json=obj, timeout = 60)
print(r.status_code, r.reason,r)
try:
    print(r.json())
except:
    pass
    
