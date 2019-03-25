import os
import requests
import pandas as pd
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="REST endpoint",default='http://escalation.sd2e.org/submission')
parser.add_argument('--csv',help="csv file")
parser.add_argument('--user',help="user name")
parser.add_argument('--expname',help="experiment name")
parser.add_argument('--crank',help="crank number [0000]")
parser.add_argument('--githash',help="7 character git commit of versioned data")
parser.add_argument('--notes',help="notes")
args=parser.parse_args()

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
    expname = commit
    
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
    print("Mut pass in 7 char githash")

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

r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},data={'crank':crank,'username':user,'expname':expname,'notes':notes, 'githash':githash},
                      files={'csvfile':open(args.csv,'rb')},timeout=60*2)    
print(r.status_code, r.reason,r)
try:
    print(r.json())
except:
    pass
