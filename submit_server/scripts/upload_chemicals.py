import sys
import csv
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="Rest endpoint",default='http://escalation.sd2e.org/admin')
parser.add_argument('--csv',help="Chemical csv")
parser.add_argument('--key',help="admin secret key",default='secret')
args=parser.parse_args()

if args.csv is None:
    print("Must pass in csv")
    exit()
    
csvfile = open(args.csv)
reader = csv.DictReader(filter(lambda row: row[0]!='#',csvfile))
inchi_arr=[]
name_arr=[]
abbrev_arr=[]
names= ('Chemical Name','Chemical Abbreviation','InChI Key (ID)')
for row in reader:
    
    if set(row.keys()) != set(names):
        print("The column names should be 'Chemical Name,Chemical Abbreviation,InChI Key (ID)'")
        exit()
    inchi_arr.append(row['InChI Key (ID)'])
    name_arr.append(row['Chemical Name'])
    abbrev_arr.append(row['Chemical Abbreviation'])

r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},data={"inchi":inchi_arr, "common_name":name_arr,"abbrev":abbrev_arr,
                                                                           "submit":"Update Chemical Names",
                                                                           "adminkey":args.key,
                                                                           },timeout=30)
print(r.status_code, r.reason,r)
try:
    print(r.json())
except:
    pass
