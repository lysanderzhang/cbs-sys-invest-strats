"""Build the reviewed local handoff with file-integrity and current visual-QA checks."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    from .validate_report import main as validate_report
    from .audit_docs import main as audit_docs
    validate_report();audit_docs()
    pdf=ROOT/'report/main.pdf';pages=len(PdfReader(pdf).pages)
    qa=json.loads((ROOT/'results/validation/pdf_visual_review.json').read_text())
    assert qa['pdf_sha256']==sha(pdf),'Inspect and record visual review of the current PDF before packaging'
    assert qa['pages_inspected']==list(range(1,pages+1)) and qa['visual_review']=='passed'
    sub=ROOT/'submission';sub.mkdir(exist_ok=True)
    shutil.copy2(pdf,sub/'HW3_Hanyu_Zhang_FINCB9339.pdf');shutil.copy2(ROOT/'report/AUDIT.md',sub/'AUDIT.md')
    shutil.copy2(ROOT/'results/audit/verification_summary.json',sub/'verification_summary.json')
    shutil.copy2(ROOT/'results/audit/compliance.csv',sub/'compliance.csv')
    # Local convenience copies use the same relative asset paths as report/main.tex.
    shutil.copy2(ROOT/'report/main.tex',sub/'final_report.tex')
    shutil.copy2(ROOT/'report/references.bib',sub/'references.bib')
    shutil.copy2(ROOT/'report/FIGURE_GUIDE.md',sub/'FIGURE_GUIDE.md')
    include=['src','tests','data','references','results','report'];files=[]
    for folder in include:
        for p in sorted((ROOT/folder).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.aux','.out','.log','.blg','.bbl']:
                files.append(p)
    files += [ROOT/name for name in ['README.md','pyproject.toml','requirements-lock.txt','.gitignore']]
    manifest={str(p.relative_to(ROOT)):sha(p) for p in files}
    (sub/'research_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=sub/'research_project.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in files:z.write(p,Path('homework3')/p.relative_to(ROOT))
        z.write(sub/'research_manifest.json','homework3/research_manifest.json')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name,digest in manifest.items():assert hashlib.sha256(z.read('homework3/'+name)).hexdigest()==digest
    v=json.loads((ROOT/'results/audit/verification_summary.json').read_text())
    (sub/'CONTENTS.md').write_text(f'''# HW3 final reviewed submission

- `HW3_Hanyu_Zhang_FINCB9339.pdf`: {pages}-page complete report with an integrated nine-figure appendix; all answers (a)-(e) on the first page and all 13 graphs included once. Submit this single PDF as the write-up.
- `final_report.tex` and `references.bib`: local, Git-ignored submission source copies; canonical sources are under `report/`. `FIGURE_GUIDE.md` identifies appendix figures.
- `AUDIT.md`: prioritized corrections, full requirement checklist, verification and unresolved limitations.
- `verification_summary.json` and `compliance.csv`: compact verification record and requirement checklist.
- `research_project.zip`: complete project rooted at `homework3/`, including source, raw inputs, references, LaTeX, daily weights/returns, all six filters, historical filter, tables, figures and tests.
- `research_manifest.json`: SHA-256 digests of the {len(files)} archived research files.

Verification: {v['tests_passed']} passing tests; {v['independent_checks']} independent checks across {v['independent_values']:,} values. All original primary numerical exports remain unchanged. The exact winning filter changes under an additional decision lag; implied-versus-historical superiority is not established statistically. See the audit for full qualifications.

To reproduce, extract the ZIP, enter `homework3/`, and follow README.md using the existing shared course environment. No project-local environment, dependency synchronization or external submission is performed. Caches, compiler executables, earlier drafts and temporary previews are excluded.

Report SHA-256: `{sha(sub/'HW3_Hanyu_Zhang_FINCB9339.pdf')}`

Archive SHA-256: `{sha(archive)}`
''')
    print(f'Final package: {pages} report pages; {len(files)} research files; {archive.stat().st_size/1024**2:.2f} MiB')

if __name__=='__main__':main()
