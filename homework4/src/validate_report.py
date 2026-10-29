"""Verify the current report's source-specific numerical bindings and completeness."""
from pathlib import Path
import hashlib,json,re
import pandas as pd
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]


def main():
    audit=json.loads((ROOT/'results/verification/independent_reconstruction.json').read_text());assert audit['all_checks_passed']
    for name,digest in audit['verified_output_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'Recompute independent reconstruction: '+name
    for row in json.loads((ROOT/'data/manifest.json').read_text()):assert hashlib.sha256((ROOT/row['copy']).read_bytes()).hexdigest()==row['sha256']
    tex=(ROOT/'report/main.tex').read_text();claims=json.loads((ROOT/'report/numerical_claims.json').read_text())
    definitions=dict(re.findall(r'\\newcommand\{\\r([A-Za-z]+)\}\{([^}]+)\}',tex))
    for c in claims:
        if c['selector'] is None:
            value=json.loads((ROOT/c['path']).read_text())
            for key in c['column'].split('.'):value=value[key]
        else:
            rows=pd.read_csv(ROOT/c['path'])
            for key,val in c['selector'].items():rows=rows[rows[key].astype(str)==str(val)]
            assert len(rows)==1;value=float(rows.iloc[0][c['column']])
        expected=f"{value*c['scale']:.{c['digits']}f}"
        assert definitions.get(c['label'])==expected and '\\r'+c['label']+'{}' in tex
    assert set(definitions)=={c['label'] for c in claims}
    log=(ROOT/'report/main.log').read_text();assert not re.search(r'Overfull|undefined|! LaTeX Error',log,re.I)
    pdf=ROOT/'report/main.pdf';assert pdf.stat().st_mtime>=(ROOT/'report/main.tex').stat().st_mtime
    reader=PdfReader(pdf);text='\n'.join(p.extract_text() for p in reader.pages);first=reader.pages[0].extract_text()
    assert all(x in first for x in ['1(a)','1(c)','2(a)','2(b)','3(a)'])
    assert not re.search(r'validation|verification|checked|no errors|checks pass|coding agent|AI workflow|placeholder|debugging',text,re.I)
    assert all(s in text for s in ['answer 1(a)','answer 1(b)','answer 1(c)','answer 2(a)','answer 2(b)','answer 3(a)','answer 3(b)','answer 3(c)','answer 3(d)'])
    assert 'FINCB9339 Systematic Investment Strategies' in first
    assert 'Homework 4: FX Returns, Compounding and Carry' in first
    assert 'References' not in text and '\\lhead' not in tex and '\\rhead' not in tex
    assert tex.count('\\includegraphics')==3
    record=dict(pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),pages=len(reader.pages),bound_narrative_quantities=len(claims),all_subquestions_present=True,all_answers_summarized_first_page=True,embedded_figures=3,latex_layout_diagnostics_clear=True)
    (ROOT/'results/verification/report_checks.json').write_text(json.dumps(record,indent=2)+'\n');print(record)

if __name__=='__main__':main()
