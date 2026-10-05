from pathlib import Path
import os
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
os.environ['JUPYTER_PATH']=str(ROOT/'build/jupyter')
os.environ['JUPYTER_RUNTIME_DIR']=str(ROOT/'build/jupyter-runtime')
os.environ['IPYTHONDIR']=str(ROOT/'build/ipython')
os.environ['MPLCONFIGDIR']=str(ROOT/'build/matplotlib')
for p in sorted((ROOT/'notebooks').glob('*.ipynb')):
    nb=nbformat.read(p,as_version=4)
    NotebookClient(nb,timeout=240,kernel_name='hw2',resources={'metadata':{'path':str(ROOT/'notebooks')}}).execute()
    nbformat.write(nb,p)
    print(p.name,'executed',sum(c.cell_type=='code' for c in nb.cells),'code cells; no errors')
