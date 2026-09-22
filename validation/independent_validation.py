"""Second implementation from source rows; deliberately imports no baseline module.

Direct historical summation replaces pandas rolling estimators. Inventory held
over price increments replaces realized-trade equity accounting. Frozen baseline
CSVs are opened only after the independent replay, for comparison.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/validation"
BASE = ROOT / "outputs/baseline"
SOURCE = Path(json.loads((BASE/"run_manifest.json").read_text())["input_path"])
TARGETS = ["2025-04-02", "2025-07-03", "2025-10-10", "2025-11-21"]
HALF_DAYS = {"2025-07-03", "2025-11-28"}


@dataclass(frozen=True)
class Case:
    name: str = "baseline_replay"
    midpoint: bool = False
    delayed: bool = False
    vwap_entry_gate: bool = False
    full_history_only: bool = False
    commission: float = .0035
    slippage: float = .001


CASES = [Case(), Case("midpoint_vwap", midpoint=True), Case("delay_30m", delayed=True),
         Case("vwap_entry_gate", vwap_entry_gate=True),
         Case("exclude_incomplete_slots", full_history_only=True),
         Case("higher_costs", commission=.005, slippage=.002)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preservation_snapshot():
    protected = [ROOT/"strategy.py", ROOT/"test_strategy.py", ROOT/"spy_replication_v0_1.zip", SOURCE]
    protected += sorted(p for p in BASE.rglob("*") if p.is_file())
    return {str(p):sha(p) for p in protected}


def source_records():
    # Row numbers assigned BEFORE sorting, preserving the original Excel address.
    x = pd.read_excel(SOURCE, sheet_name="AV.Clean")
    x["excel_row"] = np.arange(2, len(x)+2)
    d = pd.read_excel(SOURCE, sheet_name="BBRG.Daily")
    d["excel_row"] = np.arange(2, len(d)+2)
    raw = {}
    for _, r in x.iterrows():
        t = pd.Timestamp(r["Time Stamp"])
        raw[t] = dict(label=t, price=float(r["Last Price"]), volume=int(r["Volume, AV"]), row=int(r.excel_row))
    daily = {}
    for _, r in d.iterrows():
        t = pd.Timestamp(r["Time Stamp"])
        daily[t] = dict(date=t, close=float(r["Last Price"]), row=int(r.excel_row))
    dates = sorted({t.normalize() for t in raw})
    sessions = {}
    for date in dates:
        end = date + pd.Timedelta(hours=13 if str(date.date()) in HALF_DAYS else 16)
        labels = pd.date_range(date+pd.Timedelta(hours=9,minutes=30), end, freq="30min", inclusive="left")
        bars=[]
        for label in labels:
            r=raw[label]
            final = label+pd.Timedelta(minutes=30)==end
            pr=raw[end] if final else r
            bars.append(dict(date=str(date.date()), timestamp=label+pd.Timedelta(minutes=30),
                source_timestamp=label, slot=(label+pd.Timedelta(minutes=30)).strftime("%H:%M"),
                interval_price=r["price"], price=pr["price"], volume=r["volume"],
                source_row=r["row"], price_source_row=pr["row"], is_close=final,
                interval_price_cell=f"AV.Clean!B{r['row']}", volume_cell=f"AV.Clean!C{r['row']}",
                execution_price_cell=f"AV.Clean!B{pr['row']}"))
        sessions[date]=bars
    return raw,daily,dates,sessions


def independent_features(daily,dates,sessions):
    """Direct sums of individually identified observations and source addresses."""
    daily_dates=sorted(daily)
    features=[]; noise_rows=[]; vol_rows=[]; context={}
    for di,date in enumerate(dates):
        bars=sessions[date]; anchor=bars[0]
        prior=daily_dates[:daily_dates.index(date)]
        vol_dates=prior[-14:]
        returns=[]; inputs=[]
        for rd in vol_dates:
            prev=daily_dates[daily_dates.index(rd)-1]
            cc,pc=daily[rd],daily[prev]
            r=cc["close"]/pc["close"]-1
            returns.append(r)
            inputs.append(dict(target_date=str(date.date()), return_date=str(rd.date()), prior_date=str(prev.date()),
                previous_close=pc["close"], close=cc["close"], previous_close_cell=f"BBRG.Daily!D{pc['row']}",
                close_cell=f"BBRG.Daily!D{cc['row']}", spy_return=r))
        # Original BBRG.Daily columns: A blank, B timestamp, C price, D volume.
        for item in inputs:
            item["previous_close_cell"]=item["previous_close_cell"].replace("!D","!C")
            item["close_cell"]=item["close_cell"].replace("!D","!C")
        mean=math.fsum(returns)/14
        ssd=math.fsum((r-mean)**2 for r in returns)
        sigma=math.sqrt(ssd/13)
        pc=daily[prior[-1]]
        context[str(date.date())]=dict(date=str(date.date()), open_proxy=anchor["price"],
            open_source_cell=anchor["execution_price_cell"], previous_close=pc["close"],
            previous_close_cell=f"BBRG.Daily!C{pc['row']}", mean_return=mean,
            squared_deviation_sum=ssd, prior_vol=sigma, eligible=di>=14)
        if str(date.date()) in TARGETS:
            for item in inputs:
                item.update(mean_return=mean,deviation=item["spy_return"]-mean,
                            squared_deviation=(item["spy_return"]-mean)**2)
                vol_rows.append(item)
        running_v=running_pv=running_mid=0.
        prev_interval=None
        for j,b in enumerate(bars):
            moves=[]
            for histdate in dates[max(0,di-14):di]:
                hist={z["slot"]:z for z in sessions[histdate]}
                hb=hist.get(b["slot"]); ho=sessions[histdate][0]
                m=abs(hb["price"]/ho["price"]-1) if hb else None
                if m is not None: moves.append(m)
                if str(date.date()) in TARGETS:
                    noise_rows.append(dict(target_date=str(date.date()), slot=b["slot"], historical_date=str(histdate.date()),
                        open_proxy=ho["price"], open_cell=ho["execution_price_cell"],
                        historical_price=hb["price"] if hb else None,
                        price_cell=hb["execution_price_cell"] if hb else "No regular-session observation",
                        historical_source_timestamp=str(sessions[histdate][-1]["timestamp"] if hb and hb["is_close"] else hb["source_timestamp"]) if hb else None,
                        historical_available_timestamp=str(hb["timestamp"]) if hb else None,
                        absolute_move=m, available=int(hb is not None)))
            ns=math.fsum(moves)/len(moves) if di>=14 and moves else np.nan
            weight=b["interval_price"]
            midpoint=weight if prev_interval is None else (prev_interval+weight)/2
            running_v+=b["volume"]; running_pv+=weight*b["volume"]; running_mid+=midpoint*b["volume"]
            f={**b,**context[str(date.date())],"noise_sigma":ns,"noise_count":len(moves),
                "upper":max(anchor["price"],pc["close"])*(1+ns),
                "lower":min(anchor["price"],pc["close"])*(1-ns),
                "interval_price_times_volume":weight*b["volume"],"cumulative_volume":running_v,
                "cumulative_price_volume":running_pv,"vwap_endpoint":running_pv/running_v,
                "midpoint_weight_price":midpoint,"vwap_midpoint":running_mid/running_v,"is_anchor":j==0}
            features.append(f); prev_interval=weight
    return pd.DataFrame(features), pd.DataFrame(noise_rows), pd.DataFrame(vol_rows),context


def desired_position(row, held, model, case):
    if row["is_close"]: return 0
    if row["is_anchor"] or not row["eligible"]: return held
    if case.full_history_only and row["noise_count"]<14: return held
    p,u,l=row["price"],row["upper"],row["lower"]
    band=1 if p>u else (-1 if p<l else 0)
    if model=="A": return band or held
    v=row["vwap_midpoint"] if case.midpoint else row["vwap_endpoint"]
    enter=band
    if case.vwap_entry_gate:
        if enter==1 and p<=v: enter=0
        if enter==-1 and p>=v: enter=0
    breached=(held==1 and p<max(u,v)) or (held==-1 and p>min(l,v))
    if held and breached:
        return enter if enter==-held else 0
    return held if held else enter


def replay(features,model,case):
    """Mark-to-market inventory accounting, independent of realized-trade P&L."""
    capital=100000.; day_rows=[]; trades=[]; decisions=[]; events=[]
    for date,frame in features[features.eligible].groupby("date",sort=True):
        rows=frame.to_dict("records"); first=rows[0]; start=capital
        lev=min(4.,.02/first["prior_vol"]) if model=="C" else 1.
        qty=math.floor(start*lev/first["open_proxy"])
        held=0; last_price=None; entry=None; queued=None
        gross_day=comm_day=slip_day=0.
        for row in rows:
            p=row["price"]; t=row["timestamp"]; before=held
            # The old inventory earns ONLY the price increment before this decision.
            interval_gross=0. if last_price is None else held*qty*(p-last_price)
            capital+=interval_gross; gross_day+=interval_gross
            signal_time=t
            if row["is_close"]:
                target=0; queued=None
            elif case.delayed:
                target,signal_time=queued if queued else (held,t)
            else:
                target=desired_position(row,held,model,case)
            if qty==0: target=0
            units=abs(target-held)*qty
            comm=units*case.commission; slip=units*case.slippage
            capital-=comm+slip; comm_day+=comm; slip_day+=slip
            action="HOLD" if held else "FLAT"
            if target!=held:
                action="REVERSE" if held and target else ("EXIT" if held else "ENTRY")
                if held:
                    trade={"model":model,"trade_id":len(trades)+1,"date":date,"direction":held,
                        "entry_timestamp":entry["timestamp"],"exit_timestamp":t,
                        "entry_price":entry["price"],"exit_price":p,"shares":qty,
                        "sizing_leverage":lev,"start_equity":start,
                        "gross_pnl":held*qty*(p-entry["price"]),"commission":2*qty*case.commission,
                        "slippage":2*qty*case.slippage,"entry_upper":entry["upper"],"entry_lower":entry["lower"],
                        "entry_vwap":entry["vwap"],"exit_upper":row["upper"],"exit_lower":row["lower"],
                        "exit_vwap":row["vwap_midpoint"] if case.midpoint else row["vwap_endpoint"]}
                    trade["costs"]=trade["commission"]+trade["slippage"]
                    trade["net_pnl"]=trade["gross_pnl"]-trade["costs"]
                    trades.append(trade)
                    events.append({**row,"action":"EXIT","direction":held,"shares":qty,
                        "signal_timestamp":signal_time,"gross_pnl":trade["gross_pnl"],
                        "commission":qty*case.commission,"slippage":qty*case.slippage,
                        "net_pnl":trade["gross_pnl"]-qty*(case.commission+case.slippage)})
                if target:
                    entry={**row,"vwap":row["vwap_midpoint"] if case.midpoint else row["vwap_endpoint"]}
                    events.append({**row,"action":"ENTRY","direction":target,"shares":qty,
                        "signal_timestamp":signal_time,"gross_pnl":0.,"commission":qty*case.commission,
                        "slippage":qty*case.slippage,"net_pnl":-qty*(case.commission+case.slippage)})
            held=target
            if case.delayed and not row["is_close"]:
                queued=(desired_position(row,held,model,case),t)
            decisions.append({**row,"model":model,"held_before":before,"held_after":held,"action":action,
                "shares":qty,"sizing_leverage":lev,"start_equity":start,"turnover_shares":units,
                "signal_timestamp":signal_time,"interval_gross_pnl":interval_gross,"commission":comm,
                "slippage":slip,"interval_net_pnl":interval_gross-comm-slip,"marked_equity":capital,
                "long_stop":max(row["upper"],row["vwap_midpoint"] if case.midpoint else row["vwap_endpoint"]),
                "short_stop":min(row["lower"],row["vwap_midpoint"] if case.midpoint else row["vwap_endpoint"])})
            last_price=p
        assert held==0
        net=gross_day-comm_day-slip_day
        day_rows.append(dict(model=model,date=date,start_equity=start,gross_pnl=gross_day,
            commission=comm_day,slippage=slip_day,costs=comm_day+slip_day,net_pnl=net,
            equity=capital,daily_return=net/start,shares=qty,sizing_leverage=lev))
    return {"daily":pd.DataFrame(day_rows),"trades":pd.DataFrame(trades),
            "decisions":pd.DataFrame(decisions),"events":pd.DataFrame(events)}


def statistics(run):
    d,t=run["daily"],run["trades"]
    r=d.daily_return.to_numpy(); sd=float(np.std(r,ddof=1)); wealth=d.equity.to_numpy()
    peaks=np.maximum.accumulate(np.r_[100000.,wealth])[1:]
    return dict(cumulative_return=wealth[-1]/100000-1,annualized_volatility=sd*math.sqrt(252),
        sharpe=float(np.mean(r))/sd*math.sqrt(252),maximum_drawdown=float(np.min(wealth/peaks-1)),
        trades=len(t),total_costs=float(d.costs.sum()),sessions=len(d))


def trade_signature(r):
    return (str(r["date"]),int(r["direction"]),str(pd.Timestamp(r["entry_timestamp"])),
            str(pd.Timestamp(r["exit_timestamp"])),round(r["entry_price"],8),round(r["exit_price"],8))


def compare_trades(base,other):
    old=base.to_dict("records"); new=other.to_dict("records")
    signatures={trade_signature(t):t for t in new}
    old_signatures={trade_signature(t) for t in old}
    detail=[]
    for b in old:
        twin=signatures.get(trade_signature(b)); same_entry=[n for n in new if n["date"]==b["date"]
            and n["direction"]==b["direction"] and n["entry_timestamp"]==b["entry_timestamp"]]
        detail.append(dict(baseline_trade_id=b["trade_id"],date=b["date"],direction=b["direction"],
            baseline_entry=b["entry_timestamp"],baseline_exit=b["exit_timestamp"],
            baseline_shares=b["shares"],entry_or_exit_changed=twin is None,
            shares_changed_same_episode=bool(twin and twin["shares"]!=b["shares"]),
            classification="same_episode" if twin else ("same_entry_changed_exit" if same_entry else "no_identical_entry"),
            variant_exit_same_entry=same_entry[0]["exit_timestamp"] if same_entry else None,
            variant_shares_same_episode=twin["shares"] if twin else None))
    return dict(baseline_trades_changed=sum(x["entry_or_exit_changed"] for x in detail),
        baseline_trades_unchanged=sum(not x["entry_or_exit_changed"] for x in detail),
        new_or_changed_variant_trades=sum(trade_signature(t) not in old_signatures for t in new),
        shares_changed_same_episode=sum(x["shares_changed_same_episode"] for x in detail)),pd.DataFrame(detail)


def reconcile(features,runs):
    checks=[]
    f=pd.read_csv(BASE/"features.csv")
    for new,old in [("price","price"),("noise_sigma","noise_sigma"),("noise_count","noise_count"),
                    ("upper","upper"),("lower","lower"),("vwap_endpoint","vwap_approx"),
                    ("cumulative_volume","cumulative_observed_volume")]:
        error=np.nanmax(np.abs(features[new].to_numpy()-f[old].to_numpy()))
        checks.append(dict(check="features_"+new,max_absolute_error=float(error),tolerance=1e-8,passed=bool(error<1e-8)))
    for model,run in runs.items():
        frozen_d=pd.read_csv(BASE/f"{model}_daily.csv")
        frozen_t=pd.read_csv(BASE/f"{model}_trades.csv")
        assert len(frozen_d)==len(run["daily"])==168
        for field in ["gross_pnl","costs","net_pnl","equity","shares","sizing_leverage","daily_return"]:
            error=float(np.max(np.abs(frozen_d[field]-run["daily"][field])))
            tolerance=1e-7 if field in ["gross_pnl","costs","net_pnl","equity"] else 1e-10
            checks.append(dict(check=model+"_"+field,max_absolute_error=error,tolerance=tolerance,passed=error<tolerance))
        equal=[trade_signature(r) for r in frozen_t.to_dict("records")]==[trade_signature(r) for r in run["trades"].to_dict("records")]
        checks.append(dict(check=model+"_exact_trade_episodes",max_absolute_error=0 if equal else 1,tolerance=0,passed=equal))
        e=abs(run["trades"].net_pnl.sum()-run["daily"].net_pnl.sum())
        checks.append(dict(check=model+"_inventory_vs_roundtrip_pnl",max_absolute_error=e,tolerance=1e-7,passed=e<1e-7))
    frame=pd.DataFrame(checks)
    frame.to_csv(OUT/"independent_reconciliation.csv",index=False)
    if not frame.passed.all(): raise AssertionError(frame[~frame.passed].to_string())
    return frame


def concentration(day):
    total=math.prod(1+x for x in day.daily_return)-1
    profit=float(day.net_pnl.sum()); summaries=[]; selected=[]
    for tail,asc in [("best",False),("worst",True)]:
        ranked=day.sort_values(["daily_return","date"],ascending=[asc,True]).head(5)
        for rank,r in enumerate(ranked.to_dict("records"),1):
            selected.append(dict(tail=tail,rank=rank,date=r["date"],daily_return=r["daily_return"],net_pnl=r["net_pnl"],
                start_equity=r["start_equity"],dollar_pnl_share_total_profit=r["net_pnl"]/profit))
        for k in [1,3,5]:
            group=ranked.head(k)
            # Zero selected returns; preserve original 168-session horizon.
            remaining=day.copy(); remaining.loc[remaining.date.isin(group.date),"daily_return"]=0.
            without=math.prod(1+x for x in remaining.daily_return)-1
            summaries.append(dict(tail=tail,k=k,dates="; ".join(group.date),
                selected_net_pnl=group.net_pnl.sum(),selected_dollar_pnl_share=group.net_pnl.sum()/profit,
                selected_return_sum=group.daily_return.sum(),selected_compound_return=math.prod(1+x for x in group.daily_return)-1,
                baseline_cumulative_return=total,cumulative_return_without=without,
                return_difference=total-without,return_difference_share= (total-without)/total))
    return pd.DataFrame(summaries),pd.DataFrame(selected)


def export_csv(name,frame):
    frame.to_csv(OUT/f"{name}.csv",index=False,float_format="%.12f")


def main():
    OUT.mkdir(exist_ok=True,parents=True)
    before=preservation_snapshot()
    (OUT/"baseline_hashes_before.json").write_text(json.dumps(before,indent=2))
    (OUT/"predeclared_cases.json").write_text(json.dumps([asdict(c) for c in CASES],indent=2))
    raw,daily,dates,sessions=source_records()
    features,noise,vol,context=independent_features(daily,dates,sessions)
    baseline={m:replay(features,m,CASES[0]) for m in "ABC"}
    checks=reconcile(features,baseline)
    manual=baseline["C"]
    selected=manual["decisions"][manual["decisions"].date.isin(TARGETS)]
    sizing=pd.DataFrame([context[d] for d in TARGETS]).merge(manual["daily"][["date","start_equity","shares","sizing_leverage"]],on="date")
    for name,frame in [("manual_noise_history",noise),("manual_volatility_returns",vol),("manual_sizing",sizing),
        ("manual_decisions",selected),("manual_trades",manual["trades"][manual["trades"].date.isin(TARGETS)]),
        ("manual_events",manual["events"][manual["events"].date.isin(TARGETS)]),
        ("april02_1130_noise_14",noise[(noise.target_date=="2025-04-02") & (noise.slot=="11:30")]),
        ("april02_volatility_14",vol[vol.target_date=="2025-04-02"]),
        ("independent_features",features)]: export_csv(name,frame)
    results=[]; changed=[]
    for case in CASES:
        for model in "ABC":
            run=baseline[model] if case.name=="baseline_replay" else replay(features,model,case)
            comp,detail=compare_trades(baseline[model]["trades"],run["trades"])
            results.append(dict(case=case.name,model=model,**statistics(run),**comp))
            detail["case"]=case.name; detail["model"]=model; changed.append(detail)
            scenario=OUT/"scenarios"/case.name; scenario.mkdir(parents=True,exist_ok=True)
            for kind,frame in run.items(): frame.to_csv(scenario/f"{model}_{kind}.csv",index=False,float_format="%.12f")
    sensitivities=pd.DataFrame(results); export_csv("sensitivity_summary",sensitivities)
    export_csv("trade_comparison",pd.concat(changed,ignore_index=True))
    conc,ranked=concentration(manual["daily"])
    export_csv("C_concentration",conc); export_csv("C_ranked_days",ranked)
    invalid=features[features.eligible & (features.noise_count<14) & ~features.is_close & ~features.is_anchor]
    export_csv("excluded_decision_slots",invalid[["date","timestamp","slot","noise_count"]])
    tables=dict(noise=noise,volatility=vol,sizing=sizing,decisions=selected,
        trades=manual["trades"][manual["trades"].date.isin(TARGETS)],daily=manual["daily"],
        sensitivity=sensitivities,concentration=conc,ranked_days=ranked,reconciliation=checks)
    payload={key:json.loads(df.to_json(orient="records",date_format="iso",double_precision=15)) for key,df in tables.items()}
    payload["source"]=str(SOURCE); payload["case_definitions"]=[asdict(c) for c in CASES]
    (OUT/"workbook_data.json").write_text(json.dumps(payload,indent=2,allow_nan=False))
    after=preservation_snapshot()
    assert before==after,"Protected baseline changed"
    manifest=dict(baseline_unchanged=True,protected_files=len(before),source_hash=sha(SOURCE),
        validation_code_hash=sha(Path(__file__)),baseline_functions_imported=False,
        author_code_consulted=False,independence="Separate arithmetic and inventory engine; same AI and baseline conventions, not blind third-party validation",
        sessions=168,checks_passed=int(checks.passed.sum()),excluded_discretionary_slots=len(invalid),cases=[asdict(c) for c in CASES])
    (OUT/"validation_manifest.json").write_text(json.dumps(manifest,indent=2))
    print(sensitivities.to_string(index=False)); print(conc.to_string(index=False)); print(manifest)


if __name__=="__main__": main()
