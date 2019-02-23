import shutil
from tempfile import mkdtemp
import os
import time
import pandas as pd
    
    
def download_zip(basedir,files,pfx="",metadata=[]):

    tmpdir = mkdtemp()
    for f in files:
        shutil.copy(os.path.join(basedir,f), os.path.join(tmpdir,f))

        

    if pfx:
        curr = "escalation." + str(pfx) + "." + time.strftime("%Y-%m-%d-%H%M%S",time.localtime())
    else:
        curr = "escalation." + time.strftime("%Y-%m-%d-%H%M%S",time.localtime())
        
    if len(metadata) > 0:
        df = pd.DataFrame(metadata)
        df.to_csv(os.path.join(tmpdir,'metadata.csv'),index=False)
        
    shutil.make_archive(os.path.join(basedir,curr),'zip',tmpdir)
    shutil.rmtree(tmpdir)

    return os.path.join(basedir,curr+".zip")
                   
if __name__ == '__main__':
    download_zip('instance/submissions',['test.csv','test2.csv'],15,[{'a':'1','b':'2'},{'a':'3','b':'4'}])
