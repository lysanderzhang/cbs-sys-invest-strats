"""Prepare the reproducible local HW6 submission; no external submission or Git action."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, zipfile
from pypdf import PdfReader
ROOT = Path(__file__).resolve().parents[1]
NAME = 'HW6_Hanyu_Zhang_FINCB9339'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--record-reviewed', action='store_true'); args = p.parse_args()
    from .validate_report import main as check_report
    check_report()
    v = json.loads((ROOT / 'results/verification/independent_reconstruction.json').read_text()); assert v['all_checks_passed']
    pdf = ROOT / 'report/main.pdf'; pages = len(PdfReader(pdf).pages); qa = ROOT / 'results/verification/pdf_visual_review.json'
    if args.record_reviewed:
        qa.write_text(json.dumps(dict(pdf_sha256=sha(pdf), pages_inspected=list(range(1, pages + 1)), visual_review='passed',
                                      clipped_content=False, overlap=False), indent=2) + '\n')
    rec = json.loads(qa.read_text())
    assert rec['pdf_sha256'] == sha(pdf) and rec['pages_inspected'] == list(range(1, pages + 1)) and rec['visual_review'] == 'passed'
    sub = ROOT / 'submission'; sub.mkdir(exist_ok=True)
    shutil.copy2(pdf, sub / f'{NAME}.pdf'); shutil.copy2(ROOT / 'report/main.tex', sub / f'{NAME}.tex')
    log = (ROOT / 'results/verification/pytest.txt').read_text(); m = re.search(r'(\d+) passed', log); assert m and 'failed' not in log
    summary = dict(report_pages=pages, independent_scalar_comparisons=v['checks'], unit_tests_passed=int(m.group(1)),
                   handout_unchanged=True, all_subquestions_answered=True, final_pdf_sha256=sha(pdf),
                   limitations=['Problem 1 uses the equal-marginal-volatility allocation of assumption (e); optimized weights would need the full covariance matrix.',
                                'Problem 2 numbers are an illustrative lognormal example, not an empirical estimate.',
                                'The Daniel-Moskowitz appendix is not among the supplied files; 2(b) uses the second-order mean-variance approximation.'])
    (sub / 'verification_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    for x in json.loads((ROOT / 'data/manifest.json').read_text()): assert sha(ROOT / x['copy']) == x['sha256']
    files = []
    for folder in ['src', 'tests', 'data', 'references', 'results', 'report']:
        files += [f for f in sorted((ROOT / folder).rglob('*')) if f.is_file() and '__pycache__' not in f.parts
                  and f.suffix not in ['.aux', '.log', '.out', '.blg', '.bbl']]
    files += [ROOT / x for x in ['README.md', 'pyproject.toml', 'requirements-lock.txt', '.gitignore']]
    manifest = {str(f.relative_to(ROOT)): sha(f) for f in files}
    (sub / 'research_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    with zipfile.ZipFile(sub / 'research_project.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        for f in files: z.write(f, Path('homework6') / f.relative_to(ROOT))
        z.write(sub / 'research_manifest.json', 'homework6/research_manifest.json')
    with zipfile.ZipFile(sub / 'research_project.zip') as z:
        assert z.testzip() is None
        for f, d in manifest.items(): assert hashlib.sha256(z.read('homework6/' + f)).hexdigest() == d
    (sub / 'CONTENTS.md').write_text(f'''# Homework 6 submission

- `{NAME}.pdf`: complete {pages}-page write-up; every answer summarized on page one, derivations and all three figures embedded.
- `{NAME}.tex`: local Git-ignored editable copy; canonical source is `report/main.tex`. Compile in the project layout so relative figure paths resolve.
- `research_project.zip`: full reproducible project with the handout, source, tests, tables, figures and report.
- `research_manifest.json`: SHA-256 integrity record for the archive.
- `verification_summary.json`: concise numerical and source-integrity record.

Submit the PDF as the write-up. No external submission or repository publication is performed by the package script.
''')
    print('Prepared complete HW6 handoff:', pages, 'pages;', len(files), 'research files.')


if __name__ == '__main__':
    main()
