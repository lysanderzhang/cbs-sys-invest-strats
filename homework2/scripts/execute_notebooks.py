from pathlib import Path
import os,json,sys
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
shared=Path.home()/'.venvs/sys-inv/bin/python'
if Path(sys.executable)!=shared:raise RuntimeError('Use the shared FINCB9339 interpreter')
k=ROOT/'build/jupyter/kernels/sys-inv';k.mkdir(parents=True,exist_ok=True)
(k/'kernel.json').write_text(json.dumps({'argv':[str(shared),'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'FINCB9339 shared sys-inv','language':'python'}))

os.environ['JUPYTER_PATH']=str(ROOT/'build/jupyter')
os.environ['JUPYTER_RUNTIME_DIR']=str(ROOT/'build/jupyter-runtime')
os.environ['IPYTHONDIR']=str(ROOT/'build/ipython')
os.environ['MPLCONFIGDIR']=str(ROOT/'build/matplotlib')
for p in sorted((ROOT/'notebooks').glob('*.ipynb')):
    nb=nbformat.read(p,as_version=4)
    NotebookClient(nb,timeout=240,kernel_name='sys-inv',resources={'metadata':{'path':str(ROOT/'notebooks')}}).execute()
    nbformat.write(nb,p)
    print(p.name,'executed',sum(c.cell_type=='code' for c in nb.cells),'code cells; no errors')
