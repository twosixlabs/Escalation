from flask import current_app as app

import shutil
from tempfile import mkdtemp
import os
import time
import csv    

def filename(sub):
    #id, crank, username, expname
    return "%05d_%s_%s_%s.csv" %(sub.id,sub.crank,sub.username.replace(' ','-'),sub.expname.replace(' ','-'))

def download_zip(basedir,submissions,pfx=""):
    tmpdir = mkdtemp()
    metadata=[]
    for sub in submissions:
        fname = filename(sub)
        metadata.append({'user':sub.username,
                         'id': sub.id,
                         'crank':sub.crank,
                         'created':sub.created,
                         'expname':sub.expname,
                         'notes':sub.notes,
                         'filename':fname,
        })
        
    app.logger.debug(metadata)
    with open(os.path.join(tmpdir,'metadata.csv'),'w') as csvfile:
        fieldnames = ['id','user','crank','created','expname','notes','filename']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for elem in metadata:
            writer.writerow(elem)

    for sub in submissions:
        fname = filename(sub)
        fh =  open(os.path.join(tmpdir,fname),'wb')
        fh.write(sub.contents)
        fh.close()
            
    if pfx:
        curr = "escalation." + str(pfx) + "." + time.strftime("%Y%m%d-%H%M%S",time.localtime())
    else:
        curr = "escalation." + time.strftime("%Y-%m-%d-%H%M%S",time.localtime())
        
        
    shutil.make_archive(os.path.join(basedir,curr),'zip',tmpdir)
    shutil.rmtree(tmpdir)

    return os.path.join(basedir,curr+".zip")
                   
if __name__ == '__main__':
    download_zip('instance/submissions',['test.csv','test2.csv'],15,[{'id':'1','filename':'test.csv'},{'id':'2','filename':'test2.csv'}])
