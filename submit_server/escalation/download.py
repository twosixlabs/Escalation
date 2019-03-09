import shutil
from tempfile import mkdtemp
import os
import time
import csv    
    
def download_zip(basedir,files,pfx="",metadata=[]):
    tmpdir = mkdtemp()

    fileids={}
    with open(os.path.join(tmpdir,'metadata.csv'),'w') as csvfile:
        fieldnames = ['id','Crank','Created','Expname','Filename','Notes','Username']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for elem in metadata:
            writer.writerow(elem)
            fileids[elem['Filename']] = elem['id']

    for f in files:
        id = fileids[f]
        shutil.copy(os.path.join(basedir,f), os.path.join(tmpdir,"%s_%s" % (id,f)))

    if pfx:
        curr = "escalation." + str(pfx) + "." + time.strftime("%Y%m%d-%H%M%S",time.localtime())
    else:
        curr = "escalation." + time.strftime("%Y-%m-%d-%H%M%S",time.localtime())
        
        
    shutil.make_archive(os.path.join(basedir,curr),'zip',tmpdir)
    shutil.rmtree(tmpdir)

    return os.path.join(basedir,curr+".zip")
                   
if __name__ == '__main__':
    download_zip('instance/submissions',['test.csv','test2.csv'],15,[{'id':'1','filename':'test.csv'},{'id':'2','filename':'test2.csv'}])
