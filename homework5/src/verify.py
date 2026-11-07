"""Independent scalar reconstruction from frozen daily JSON; no production finance imports."""
import csv, hashlib, json, math, statistics
from datetime import datetime
from zoneinfo import ZoneInfo
from .config import ROOT
# Independently stated universe and module structure.
PAIRS=[("VTI","EFA"),("HYG","LQD"),("VNQ","REM"),("GLD","TLT")]
ASSETS=[a for pair in PAIRS for a in pair]+["SHV"]

def main():
    snapshots={}
    for a in ASSETS:
        j=json.loads((ROOT/"data/raw"/f"{a}.json").read_text())["chart"]["result"][0]
        months={}
        for ts,value in zip(j["timestamp"],j["indicators"]["adjclose"][0]["adjclose"]):
            date=datetime.fromtimestamp(ts,ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
            if date<="2026-06-30": months[date[:7]]=float(value)
        snapshots[a]=months
    months=sorted(set.intersection(*(set(x) for x in snapshots.values())))
    expected={}
    weights={}
    examples=[]
    for n in range(13,len(months)):
        month=months[n]; decision=months[n-1]; old=months[n-13]
        w={a:0. for a in ASSETS}
        cashscore=snapshots["SHV"][decision]/snapshots["SHV"][old]-1
        for pair in PAIRS:
            mom={a:snapshots[a][decision]/snapshots[a][old]-1 for a in pair}
            best=max(pair,key=lambda a:mom[a])
            chosen=best if mom[best]>cashscore else "SHV"
            w[chosen]+=.25
        r={a:snapshots[a][month]/snapshots[a][decision]-1 for a in ASSETS}
        expected[month]=math.fsum(w[a]*r[a] for a in ASSETS)
        weights[month]=w
        if n in [13,18,len(months)-1]:examples.append({"month":month,"decision_month":decision,"lookback_base":old,"return":expected[month],"weights":w})
    observed=list(csv.DictReader((ROOT/"results/timeseries/portfolio_returns.csv").open()))
    wh=list(csv.DictReader((ROOT/"results/timeseries/weights_dual.csv").open()))
    errors=[]
    checks=0
    for row,wrow in zip(observed,wh,strict=True):
        month=row[""][0:7]
        errors.append(abs(float(row["Dual"])-expected[month]));checks+=1
        for a in ASSETS:
            assert abs(float(wrow[a])-weights[month][a])<1e-14
            checks+=1
    assert len(observed)==len(expected)==217
    assert max(errors)<1e-12
    vals=list(expected.values())
    wealth=1.;peak=1.;dd=0.
    for r in vals:
        wealth*=1+r;peak=max(peak,wealth);dd=min(dd,wealth/peak-1)
    cash=[float(row["Cash"]) for row in observed]
    ex=[r-c for r,c in zip(vals,cash)]
    perf=list(csv.DictReader((ROOT/"results/tables/performance.csv").open()))
    full=next(x for x in perf if x["strategy"]=="Dual" and x["period"]=="Full")
    independent={"cagr_pct":100*(wealth**(12/len(vals))-1),"arithmetic_pct":1200*statistics.mean(vals),"volatility_pct":100*statistics.stdev(vals)*math.sqrt(12),"sharpe":statistics.mean(ex)/statistics.stdev(ex)*math.sqrt(12),"max_drawdown_pct":100*dd,"terminal_wealth":wealth}
    # Quantile convention is linear interpolation of the ordered observations.
    ordered=sorted(vals); pos=.05*(len(vals)-1);low=int(pos)
    cutoff=ordered[low]+(pos-low)*(ordered[low+1]-ordered[low])
    independent["var5_pct"]=100*cutoff
    independent["es5_pct"]=100*statistics.mean([v for v in vals if v<=cutoff])
    for k,v in independent.items():
        assert abs(v-float(full[k]))<1e-10,(k,v,full[k])
        checks+=1
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ["results/tables","results/timeseries","data/processed"] for p in sorted((ROOT/folder).glob("*.csv"))}
    out={"scalar_comparisons":checks,"maximum_return_difference":max(errors),"representative_reconstructions":examples,"independent_metrics":independent,"output_sha256":hashes}
    (ROOT/"results/verification/independent.json").write_text(json.dumps(out,indent=2)+"\n")
    print(checks,"independent comparisons; max return difference",max(errors))
if __name__=="__main__":main()
