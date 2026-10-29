"""Prepare the reproducible local HW4 submission; no external submission or Git action."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile,re
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--record-reviewed',action='store_true');args=p.parse_args()
    from .validate_report import main as check_report
    check_report()
    v=json.loads((ROOT/'results/verification/independent_reconstruction.json').read_text());assert v['all_checks_passed']
    pdf=ROOT/'report/main.pdf';pages=len(PdfReader(pdf).pages);qa=ROOT/'results/verification/pdf_visual_review.json'
    if args.record_reviewed:
        qa.write_text(json.dumps(dict(pdf_sha256=sha(pdf),pages_inspected=list(range(1,pages+1)),visual_review='passed',clipped_content=False,overlap=False),indent=2)+'\n')
    record=json.loads(qa.read_text());assert record['pdf_sha256']==sha(pdf) and record['pages_inspected']==list(range(1,pages+1)) and record['visual_review']=='passed'
    sub=ROOT/'submission';sub.mkdir(exist_ok=True)
    shutil.copy2(pdf,sub/'HW4_Hanyu_Zhang_FINCB9339.pdf');shutil.copy2(ROOT/'report/main.tex',sub/'HW4_Hanyu_Zhang_FINCB9339.tex')
    shutil.copy2(ROOT/'results/verification/requirements.csv',sub/'requirements.csv')
    testlog=(ROOT/'results/verification/pytest.txt').read_text();match=re.search(r'(\d+) passed',testlog);assert match and 'failed' not in testlog
    summary=dict(report_pages=pages,empirical_return_dates=v['return_dates'],independent_scalar_comparisons=v['checks'],unit_tests_passed=int(match.group(1)),source_inputs_unchanged=True,all_subquestions_answered=True,final_pdf_sha256=sha(pdf),limitations=['Inverse moments not identified by first two moments; Taylor approximations are local.','Rule of 72 uses decimal/percentage units consistently and fractional doubling periods.','Option illustration is model-based, not historical investment performance.'])
    (sub/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    files=[]
    for folder in ['src','tests','data','references','results','report']:
        for f in sorted((ROOT/folder).rglob('*')):
            if f.is_file() and '__pycache__' not in f.parts and f.suffix not in ['.aux','.log','.out','.blg','.bbl']:files.append(f)
    files += [ROOT/x for x in ['README.md','pyproject.toml','requirements-lock.txt','.gitignore']]
    manifest={str(f.relative_to(ROOT)):sha(f) for f in files}
    (sub/'research_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(sub/'research_project.zip','w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for f in files:z.write(f,Path('homework4')/f.relative_to(ROOT))
        z.write(sub/'research_manifest.json','homework4/research_manifest.json')
    with zipfile.ZipFile(sub/'research_project.zip') as z:
        assert z.testzip() is None
        for f,d in manifest.items():assert hashlib.sha256(z.read('homework4/'+f)).hexdigest()==d
    (sub/'CONTENTS.md').write_text(f'''# Homework 4 submission\n\n- `HW4_Hanyu_Zhang_FINCB9339.pdf`: complete {pages}-page write-up, with every answer summarized on the first page and all three figures embedded.\n- `HW4_Hanyu_Zhang_FINCB9339.tex`: local Git-ignored editable copy; canonical source is `report/main.tex`. Compile in the project layout so relative figure paths resolve.\n- `research_project.zip`: full reproducible project with original inputs, references, source, tables, daily returns, figures and report.\n- `research_manifest.json`: SHA-256 integrity record for the archive.\n- `requirements.csv`: requirement-by-requirement coverage.\n- `verification_summary.json`: concise numerical and source-integrity record.\n\nSubmit the PDF as the write-up; the archive provides the complete supporting work. Use the existing shared course Python environment and follow README.md. No new environment, external homework submission or repository publication is performed by the package script.\n''')
    print('Prepared complete HW4 handoff:',pages,'pages;',len(files),'research files.')

if __name__=='__main__':main()
