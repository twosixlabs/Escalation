from flask import current_app as app
import shutil
from tempfile import mkdtemp
import os
import csv
import random
import time
default_models = [
    'BOGP',
    'gradient_boosted_tree',
    'support_vector_radial_basis_classifier',
    'random_forest_classification',
    'baseline_uniform'
    ]

def download_uniform_policy(basedir,submissions,size,pfx=""):
    app.logger.info("Running uniform sampling policy")
    target_size = size // len(submissions)
    targets=[]
    remainder = size % len(submissions)
    for i in range(len(submissions)):
        targets.append(target_size + 1 if i < remainder else target_size)
    for i in range(len(targets)):
        app.logger.info("Selected %d rows for %s" % (targets[i], submissions[i].expname))
        
    tmpdir = mkdtemp()
    metadata=[]
    for sub in submissions:
        metadata.append({'user':sub.username,
                         'id': sub.id,
                         'crank':sub.crank,
                         'created':sub.created,
                         'expname':sub.expname,
                         'notes':sub.notes,
        })
        
    with open(os.path.join(tmpdir,'metadata.csv'),'w') as csvfile:
        fieldnames = ['id','user','crank','created','expname']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n',extrasaction='ignore')
        writer.writeheader()
        for elem in metadata:
            writer.writerow(elem)

    seen={}
    with open(os.path.join(tmpdir,'submission.csv'),'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['dataset','name','predicted_out','score','expname'],extrasaction='ignore',lineterminator='\n')        
        writer.writeheader()
        for idx, sub in enumerate(submissions):
            preds = [p.__dict__ for p in sub.rows] #map to dict for csv.dictwriter
            random.shuffle(preds)
            c = 0
            for p in preds:
                if p['name'] in seen:
                    continue
                seen[p['name']] = 1
                if p['predicted_out'] == 0:
                    p['predicted_out'] = 'null'

                p['expname'] = sub.expname                    
                writer.writerow(p)
                c+=1                
                if c >= targets[idx]:
                    break
            app.logger.info("Writing %d of %d predictions for %s" % (c,len(preds), sub))
            
    if pfx:
        curr = "escalation." + str(pfx) + "." + time.strftime("%Y%m%d-%H%M%S",time.localtime())
    else:
        curr = "escalation." + time.strftime("%Y-%m-%d-%H%M%S",time.localtime())
        
    shutil.make_archive(os.path.join(basedir,curr),'zip',tmpdir)
    shutil.rmtree(tmpdir)

    return os.path.join(basedir,curr+".zip"), "Selected %d predictions per %d models, resulting in %d total" %(target_size, len(submissions), len(seen))
