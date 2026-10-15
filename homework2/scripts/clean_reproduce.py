"""Cached clean rerun: forbid HTTP, regenerate all numeric outputs, compare hashes."""
from pathlib import Path
import sys,json,hashlib,datetime,contextlib,io
import yaml,requests
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def forbid(*a,**k):raise RuntimeError('Network attempted in offline reproduction')
requests.sessions.Session.request=forbid
cfg=yaml.safe_load((ROOT/'config/base.yaml').read_text())
from momentum_hw2.pipeline import run
from momentum_hw2.data_validation import validate
from momentum_hw2.reporting import report
paths=list((ROOT/'results/tables').glob('*.csv'))+list((ROOT/'results/audits').glob('*decisions.csv'))+list((ROOT/'results/audits').glob('*targets.csv'))+list((ROOT/'results/audits').glob('*trades.csv'))+list((ROOT/'results/audits').glob('*holdings_daily.csv'))
before={str(p.relative_to(ROOT)):digest(p) for p in paths}
log=io.StringIO()
with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    print('Cached clean reproduction UTC',datetime.datetime.now(datetime.timezone.utc).isoformat())
    print('HTTP disabled; no fetch/import calls; inputs frozen.')
    validate(cfg)
    run(cfg)
    report(cfg)
    after={str(p.relative_to(ROOT)):digest(p) for p in paths}
    mismatch=[p for p in before if before[p]!=after[p]]
    print('Compared',len(paths),'numeric tables/audits; mismatches:',mismatch)
    print('PASS' if not mismatch else 'FAIL')
(ROOT/'results/audits/clean_run.log').write_text(log.getvalue())
(ROOT/'results/audits/reproduction_hashes.json').write_text(json.dumps({'before':before,'after':after,'mismatch':mismatch,'status':'PASS' if not mismatch else 'FAIL'},indent=2))
print(log.getvalue())
if mismatch:raise SystemExit(1)
