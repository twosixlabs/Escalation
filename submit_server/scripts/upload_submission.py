import os
import requests
import pandas as pd
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="REST endpoint",default='http://escalation.sd2e.org/submission')
parser.add_argument('--dev',help="Use dev manifest and dev endpoint",action='store_true')
parser.add_argument('--csv',help="csv file")
parser.add_argument('--user',help="user name")
parser.add_argument('--expname',help="experiment name")
parser.add_argument('--crank',help="crank number [0000]")
parser.add_argument('--githash',help="7 character git commit of versioned data")
parser.add_argument('--notes',help="notes")
args=parser.parse_args()

if args.dev and args.endpoint == 'http://escalation.sd2e.org/submission':
    args.endpoint = 'http://escalation-dev.sd2e.org/submission'
    
if not args.dev:
    while True:
        a = input("Uploading to production server. Are you sure? [yes/no]:")
        if a == "yes":
            break
        elif a == "no":
            exit()
print("Uploading to",args.endpoint)

regex=r'(\d{4})_train_([^-]{7})_([^\.]+)\.csv'

crank = None
githash = None
user = None
expname = None

m = re.search(regex,args.csv)
if m:
    crank = m.group(1)
    githash = m.group(2)
    user = m.group(3)
    expname = githash
    
elif args.crank == None:
    print("Can't extract data from CSV, must pass in --crank")
    exit()
elif args.user == None:
    print("Can't extract data from CSV, must pass in --user")
    exit()    
elif args.expname == None or ' ' in args.expname:
    print("Must pass in experiment name and not have spaces")
    exit()
elif args.csv == None:
    print("Must pass in csv file")
    exit()
elif args.githash == None:
    print("Mut pass in 7 char githash from versioned-data")
    exit()
    
notes = args.notes or ""
if expname is None:
    expname = args.expname
    
if crank is None:
    crank = args.crank
    
if user is None:
    user = args.user

if githash is None:
    githash = args.githash
    
print("crank:",crank)
print("username:",user)
print("expname:",expname)
print("notes:",notes)
print("csv:",args.csv)
print("githash:",githash)

print("If you are uploading 1000s of rows, this may take a couple minutes due to input validation")
r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},data={'crank':crank,'username':user,'expname':expname,'notes':notes, 'githash':githash},
                      files={'csvfile':open(args.csv,'rb')},timeout=60*5)    
print(r.status_code, r.reason,r)
try:
    out = r.json()
    
    if 'error' in out:
        if type(out['error']) == list:
            print( "\n".join(out['error']))
        else:
            print(out['error'])
except:
    pass
