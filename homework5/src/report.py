"""Generate the report directly from exported numerical results."""
import json, hashlib
import pandas as pd
from .config import ROOT

def main():
    perf=pd.read_csv(ROOT/"results/tables/performance.csv")
    def row(name,period="Full"):
        return perf[(perf.strategy==name)&(perf.period==period)].iloc[0]
    def n(name,key,period="Full"):return f"{row(name,period)[key]:.5f}"
    def table(headers,rows,align=None):
        align=align or "l"+"r"*(len(headers)-1)
        lines=[r"\begin{center}\small\begin{tabular}{"+align+r"}\toprule"," & ".join(headers)+r"\\\midrule"]
        for cells in rows:lines.append(" & ".join(str(c) for c in cells)+r"\\")
        lines.append(r"\bottomrule\end{tabular}\end{center}")
        return "\n".join(lines)
    def perftable(names,period="Full"):
        return table(["Portfolio","CAGR (\\%)","Vol. (\\%)","Sharpe","MDD (\\%)"],[[name]+[n(name,k,period) for k in ["cagr_pct","volatility_pct","sharpe","max_drawdown_pct"]] for name in names])
    tokens={}
    tokens["PERFORMANCE"]=perftable(["Dual","Relative","Absolute","Static","Buffer","US equities","Exposure control"])
    tokens["TAILS"]=table(["Portfolio","Arith. (\\%)","Worst (\\%)","ES$_{5\\%}$ (\\%)","Skew","Ex. kurt."],[[a]+[n(a,k) for k in ["arithmetic_pct","worst_month_pct","es5_pct","skewness","excess_kurtosis"]] for a in ["Dual","Relative","Absolute","Static","Buffer"]])
    tokens["MODULES"]=perftable(["Equities","Credit","REITs","Stress"])
    comp=pd.read_csv(ROOT/"results/tables/module_comparison.csv")
    tokens["MODULEAB"]=table(["Module","Rule","CAGR (\\%)","Sharpe","MDD (\\%)"],[[x.module,x.mode]+[f"{getattr(x,k):.5f}" for k in ["cagr_pct","sharpe","max_drawdown_pct"]] for x in comp.sort_values(["module","mode"]).itertuples() if x.mode in ["dual","relative","static"]])
    lit=pd.read_csv(ROOT/"results/tables/paper_table10.csv").set_index("strategy")
    tokens["PAPER"]=table(["Module","Paper return","ETF CAGR","Paper SR","ETF SR"],[[a if a!="Dual" else "Composite",f"{lit.loc[a,'annual_return_pct']:.5f}",n(a,"cagr_pct"),f"{lit.loc[a,'sharpe']:.5f}",n(a,"sharpe")] for a in ["Equities","Credit","REITs","Stress","Dual"]])
    tokens["SUBPERIOD"]=table(["Window","Strategy","Months","CAGR (\\%)","Sharpe","MDD (\\%)"],[[lab,a,int(row(a,p)["months"]),n(a,"cagr_pct",p),n(a,"sharpe",p),n(a,"max_drawdown_pct",p)] for p,lab in [("Overlap to 2011","2008--2011"),("Extension 2012+","2012--2026")] for a in ["Dual","Relative","Static","US equities"]])
    tokens["STRESS"]=table(["Window","Strategy","Wealth return (\\%)","MDD (\\%)"],[[p,a,f"{100*(row(a,p)['terminal_wealth']-1):.5f}",n(a,"max_drawdown_pct",p)] for p in ["Crisis 2008-09","2020","2022","2026 H1"] for a in ["Dual","Static","US equities"]])
    lag=pd.read_csv(ROOT/"results/tables/lag_common_sample.csv")
    tokens["LAG"]=table(["Timing, July 2008--June 2026","CAGR (\\%)","Sharpe","MDD (\\%)"],[[x.strategy]+[f"{getattr(x,k):.5f}" for k in ["cagr_pct","sharpe","max_drawdown_pct"]] for x in lag.itertuples()])
    costs=pd.read_csv(ROOT/"results/tables/cost_sensitivity.csv")
    tokens["COSTS"]=table(["Strategy","Cost (bp)","Traded/yr (\\%)","CAGR (\\%)","Sharpe"],[[x.strategy,int(x.cost_bps_per_dollar)]+[f"{getattr(x,k):.5f}" for k in ["annual_traded_pct","cagr_pct","sharpe"]] for x in costs.itertuples()])
    boot=pd.read_csv(ROOT/"results/tables/bootstrap.csv")
    tokens["BOOT"]=table(["Extension Sharpe difference","95\\% lower","95\\% upper"],[[x.comparison,f"{x.lower95:.5f}",f"{x.upper95:.5f}"] for x in boot.itertuples()])
    corr=pd.read_csv(ROOT/"results/tables/module_correlation.csv",index_col=0)
    tokens["CORR"]=table(["Module"]+list(corr),[[a]+[f"{v:.5f}" for v in corr.loc[a]] for a in corr.index])
    util=pd.read_csv(ROOT/"results/tables/utilization.csv")
    tokens["USE"]=table(["Module","First risky asset (\\%)","Second risky asset (\\%)","SHV (\\%)"],[[m]+[f"{v:.5f}" for v in util[util.module==m].allocation_pct] for m in ["Equities","Credit","REITs","Stress"]])
    hold=pd.read_csv(ROOT/"results/tables/representative_holdings.csv",index_col=0)
    cells=[]
    for d,x in hold.iterrows():cells.append([d,", ".join(f"{a}: {v*100:.0f}\\%" for a,v in x.items() if v>0)])
    tokens["HOLDINGS"]=table(["Return month ending","Holdings at preceding month-end"],cells,"lp{10cm}")
    q=pd.read_csv(ROOT/"results/tables/data_quality.csv")
    tokens["COVERAGE"]=table(["Asset","First daily quote","Last quote","Daily rows"],[[x.asset,x.first,x.last,x.rows] for x in q.itertuples()])
    tokens["RISK"]=f"{json.loads((ROOT/'results/summary.json').read_text())['average_risky_allocation_pct']:.5f}"
    tokens["GROWTH"]=n("Dual","terminal_wealth")
    tokens["CONTROLDD"]=n("Exposure control","max_drawdown_pct")
    source=(ROOT/"report/template.tex").read_text()
    narrative={}
    for literal,name,key,period in [
        ("6.08340","Dual","cagr_pct","Full"),("0.58737","Dual","sharpe","Full"),
        ("-14.05541","Dual","max_drawdown_pct","Full"),("0.48750","Static","sharpe","Full"),
        ("6.52178","Static","cagr_pct","Full"),("0.51158","Dual","sharpe","Extension 2012+"),
        ("0.54822","Static","sharpe","Extension 2012+"),("6.33698","Buffer","cagr_pct","Full"),
        ("0.61771","Buffer","sharpe","Full")]:
        narrative[literal]={"value":float(row(name,period)[key]),"source":"results/tables/performance.csv","strategy":name,"period":period,"field":key}
    for literal,name,field in [("430.67160","Dual","annual_traded_pct"),("353.81480","Buffer","annual_traded_pct"),("5.62734","Dual","cagr_pct"),("5.96127","Buffer","cagr_pct")]:
        x=costs[(costs.strategy==name)&(costs.cost_bps_per_dollar==10)].iloc[0]
        narrative[literal]={"value":float(x[field]),"source":"results/tables/cost_sensitivity.csv","strategy":name,"cost_bps_per_dollar":10,"field":field}
    traded=costs[costs.cost_bps_per_dollar==0].set_index("strategy").annual_traded_pct
    narrative["17.84580"]={"value":float(100*(1-traded.Buffer/traded.Dual)),"source":"results/tables/cost_sensitivity.csv","formula":"100*(1-Buffer/Dual annual_traded_pct), cost=0"}
    narrative["0.29672"]={"value":float(-row("Cash")["max_drawdown_pct"]),"source":"results/tables/performance.csv","strategy":"Cash","field":"negative max_drawdown_pct","period":"Full"}
    for literal,meta in narrative.items():
        if literal not in source: raise ValueError(f"Narrative anchor absent: {literal}")
        source=source.replace(literal,f"{meta['value']:.5f}")
    for k,v in tokens.items():source=source.replace("@@"+k+"@@",v)
    if "@@" in source:raise ValueError("Unresolved report token")
    (ROOT/"report/main.tex").write_text(source)
    evidence={"narrative":narrative,"table_sections":list(tokens),"main_tex_sha256":hashlib.sha256(source.encode()).hexdigest()}
    (ROOT/"results/verification/report_evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
    print("Generated report from",len(tokens),"result-linked sections.")
if __name__=="__main__":main()
