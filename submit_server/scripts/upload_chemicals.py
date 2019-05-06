import sys
import csv
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="Rest endpoint",default='http://escalation.sd2e.org/admin')
parser.add_argument('--tsv',help="Chemical tab separated tsv")
parser.add_argument('--key',help="admin secret key",default='Trompdoy')
args=parser.parse_args()

if args.tsv is None:
    print("Must pass in tsv")
    exit()
    
tsvfile = open(args.tsv)
reader = csv.DictReader(filter(lambda row: row[0]!='#',tsvfile),delimiter="\t")
inchi_arr=[]
name_arr=[]
abbrev_arr=[]
id_arr=[]
i=0
names= ('Chemical Name','Chemical Abbreviation','InChI Key (ID)')
for i, row in enumerate(reader):

    for name in names:
        if name not in row:
            print("Column '%s' not found in tsv" % name)
            exit()
    if row['InChI Key (ID)'] == "" or row['InChI Key (ID)'] == None or row['InChI Key (ID)'] == 'null':
        print("Skipping row %d because of invalid InChI Key (ID) '%s'" % (i,row['InChI Key (ID)']))
        continue
    if row['Chemical Name'] == "" or row['Chemical Name'] == None or row['Chemical Name'] == 'null':
        print("Skipping row %d because of invalid chemical name '%s'" % (i,row['Chemical Name']))
        continue
    if row['Chemical Abbreviation'] == "" or row['Chemical Abbreviation'] == None or row['Chemical Abbreviation'] == 'null':
        print("Skipping row %d because of invalid Chemical Abbreviation '%s'" % (i, row['Chemical Abbreviation']))
        continue    
    inchi_arr.append(row['InChI Key (ID)'])
    name_arr.append(row['Chemical Name'])
    abbrev_arr.append(row['Chemical Abbreviation'])
    i+=1
    id_arr.append(i)

r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},data={"inchi":inchi_arr, "common_name":name_arr,"abbrev":abbrev_arr,"id":id_arr,
                                                                           "submit":"Update Chemical Names",
                                                                           "adminkey":args.key,
                                                                           },timeout=30)
print(r.status_code, r.reason,r)
try:
    print(r.json())
except:
    pass
