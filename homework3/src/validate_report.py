"""Verify each narrative macro against its specified dataset, row, metric and units."""
from pathlib import Path
import json,re,hashlib
import pandas as pd
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]

def validate_bindings(tex,claims):
    found=dict(re.findall(r'\\newcommand\{\\r([A-Za-z]+)\}\{([^}]+)\}',tex))
    cache={}
    for claim in claims:
        path=claim['path']
        if path not in cache:cache[path]=pd.read_csv(ROOT/path)
        rows=cache[path]
        for key,value in claim['selector'].items():rows=rows[rows[key].astype(str)==str(value)]
        if len(rows)!=1:raise ValueError('Ambiguous source binding: '+claim['label'])
        value=(float(rows.iloc[0][claim['column']])+claim['offset'])*claim['scale']
        expected=f"{value:.{claim['digits']}f}"
        if found.get(claim['label'])!=expected:raise ValueError('Incorrect source/metric/unit binding: '+claim['label'])
        if '\\r'+claim['label']+'{}' not in tex:raise ValueError('Unused result claim: '+claim['label'])
    if set(found)!=set(c['label'] for c in claims):raise ValueError('Undeclared narrative numerical macro')
    return len(claims)

def main():
    verified=json.loads((ROOT/'results/audit/verified_file_hashes.json').read_text())
    for name,digest in verified.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('Re-run independent review: stale verified file '+name)
    texpath=ROOT/'report/main.tex';assert not re.search(rb'[\x00-\x08\x0b-\x1f]',texpath.read_bytes()), 'Unexpected source control character';tex=texpath.read_text();claims=json.loads((ROOT/'report/numerical_claims.json').read_text())
    n=validate_bindings(tex,claims)
    log=(ROOT/'report/main.log').read_text()
    if re.search(r'Overfull|Citation .*undefined|Reference .*undefined|! LaTeX Error',log):raise ValueError('Unresolved LaTeX diagnostics')
    pdfpath=ROOT/'report/main.pdf'
    if pdfpath.stat().st_mtime<texpath.stat().st_mtime:raise ValueError('Compiled PDF is older than its source')
    pdf=PdfReader(pdfpath);first=pdf.pages[0].extract_text()
    assert all(v in first for v in ['(a)','(b)','(c)','(d)','(e)'])
    text='\n'.join(p.extract_text() for p in pdf.pages)
    assert not re.search(r'coding agent|AI workflow|placeholder|debugging',text,re.I)
    from .appendix import FIGURES
    for name,_,_ in FIGURES:
        assert tex.count('../results/figures/'+name+'.pdf')==1, 'Missing or duplicate appendix figure: '+name
    assert 'Additional graphical evidence' in text and 'Figure A.9' in text
    assert len(re.findall(r'\\includegraphics',tex))==13
    assert not re.search(r'\b(?:validation|verification|reconciled|checked)\b|checks pass|no errors|audit/checklist|shared course environment|README', text, re.I), 'Remove development-process wording from the final report'
    verification=json.loads((ROOT/'results/audit/verification.json').read_text());assert verification['all_checks_passed']
    result=dict(source_bound_claims=n,source_row_metric_and_units_verified=True,compiled_pdf_pages=len(pdf.pages),
        all_answers_on_first_page=True,integrated_appendix_figures=9,total_figures=13,latex_overfull_boxes=0,independent_checks=verification['checks'],independent_values=verification['values_checked'])
    (ROOT/'results/validation/report_numerical_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)

if __name__=='__main__':main()
