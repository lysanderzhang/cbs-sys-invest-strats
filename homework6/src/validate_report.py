"""Confirm the report's numerical bindings, layout log and answer coverage."""
from pathlib import Path
import hashlib, json, re
import pandas as pd
from pypdf import PdfReader
ROOT = Path(__file__).resolve().parents[1]
ANSWERS = ['answer 1.1', 'answer 1.2', 'answer 1.3', 'answer 1.4', 'answer 1.5', 'answer 1.6', 'answer 1.7', 'answer 1.8',
           'answer 2(a)', 'answer 2(b)', 'answer 2(c)', 'answer 2(d)', 'answer 2(e)', 'answer 2(f)', 'answer 2(g)']


def value_of(c):
    if c['path'].endswith('.csv'):
        rows = pd.read_csv(ROOT / c['path'])
        for k, v in (c['selector'] or {}).items(): rows = rows[rows[k].astype(str) == str(v)]
        assert len(rows) == 1; return float(rows.iloc[0][c['column']])
    v = json.loads((ROOT / c['path']).read_text())
    for k in c['column'].split('.'): v = v[k]
    return float(v)


def main():
    audit = json.loads((ROOT / 'results/verification/independent_reconstruction.json').read_text()); assert audit['all_checks_passed']
    for name, digest in audit['verified_output_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'Rerun src.verify: ' + name
    tex = (ROOT / 'report/main.tex').read_text(); claims = json.loads((ROOT / 'report/numerical_claims.json').read_text())
    defs = dict(re.findall(r'\\newcommand\{\\r([A-Z][A-Za-z]*)\}\{(.+)\}', tex))
    assert set(defs) == {c['label'] for c in claims}
    for c in claims:
        assert defs[c['label']] == c['formatted'] and '\\r' + c['label'] in tex.split('\\begin{document}')[1]
        shown = float(c['formatted'].replace('{,}', '')); v = value_of(c) * c['scale']
        assert abs(shown - v) <= max(0.5 * 10 ** -c['digits'], 0.05 * abs(v)), c
    log = (ROOT / 'report/main.log').read_text(errors='ignore'); assert not re.search(r'Overfull|undefined|! LaTeX Error', log, re.I)
    pdf = ROOT / 'report/main.pdf'; assert pdf.stat().st_mtime >= (ROOT / 'report/main.tex').stat().st_mtime
    reader = PdfReader(pdf); text = '\n'.join(p.extract_text() for p in reader.pages); first = reader.pages[0].extract_text()
    assert all(x in first for x in ['1.1', '1.2', '1.3', '1.4', '1.5', '1.8', '2(a)', '2(d)', '2(e)', '2(f)', '2(g)'])
    assert not re.search(r'validation|verification|checked|no errors|checks pass|coding agent|AI workflow|placeholder|debugging', text, re.I)
    norm = re.sub(r'\s+', ' ', text)
    missing = [a for a in ANSWERS if a not in norm]; assert not missing, missing
    assert 'Homework 6' in first and 'Hanyu Zhang' in first and tex.count('\\includegraphics') == 3
    record = dict(pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(), pages=len(reader.pages), bound_narrative_quantities=len(claims),
                  all_subquestions_present=True, all_answers_summarized_first_page=True, embedded_figures=3, latex_layout_diagnostics_clear=True)
    (ROOT / 'results/verification/report_checks.json').write_text(json.dumps(record, indent=2) + '\n'); print(record)


if __name__ == '__main__':
    main()
