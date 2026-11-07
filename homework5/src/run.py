import json, importlib.metadata
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from .config import ROOT, ASSETS, CASH, MODULES
from .data import load
from .strategy import holdings, statistics, turnover

def save(df,path,index=True): df.to_csv(ROOT/path,index=index,float_format="%.17g",date_format="%Y-%m-%d")

def main():
    daily,prices,quality=load()
    save(daily,"data/processed/daily_adjusted_close.csv")
    save(prices,"data/processed/monthly_adjusted_close.csv")
    save(quality,"results/tables/data_quality.csv",False)
    returns=prices.pct_change(fill_method=None)
    save(returns,"results/timeseries/asset_returns.csv")
    modes={"Dual":"dual","Relative":"relative","Absolute":"absolute","Static":"static","Buffer":"buffer"}
    weights, series, modules={}, {}, {}
    for name,mode in modes.items():
        w,r,s,md=holdings(prices,mode)
        weights[name]=w;series[name]=r
        save(w,f"results/timeseries/weights_{mode}.csv")
        if name=="Dual":
            save(s,"results/timeseries/momentum_12m.csv")
            md["return_date"]=md.decision_date+pd.offsets.MonthEnd(1)
            md=md[md.return_date<=prices.index[-1]]
            save(md,"results/timeseries/module_holdings.csv",False)
            for m in MODULES:
                mw=md.loc[md.module==m].set_index("return_date")[ASSETS]
                modules[m]=(mw*returns.loc[mw.index]).sum(axis=1)
    out=pd.DataFrame(series)
    idx=out.index
    asset=returns.loc[idx]
    out["US equities"]=asset.VTI
    out["Cash"]=asset.SHV
    risk=1-weights["Dual"][CASH].mean()
    out["Exposure control"]=risk*asset.drop(columns=CASH).mean(axis=1)+(1-risk)*asset[CASH]
    lag=weights["Dual"].reindex(prices.index).shift(1).loc[idx].dropna()
    out["Extra month lag"]=(lag*returns.loc[lag.index]).sum(axis=1)
    trades={}
    cost_rows=[]
    for name in ["Dual","Buffer"]:
        tr=turnover(weights[name],returns.loc[idx])
        trades[name]=tr
        for bps in [0,10,25]:
            net=(1-bps/10000*tr)*(1+out[name])-1
            cost_rows.append({"strategy":name,"cost_bps_per_dollar":bps,"annual_traded_pct":1200*tr.mean(),**statistics(net,asset[CASH])})
    save(pd.DataFrame(trades),"results/timeseries/turnover.csv")
    save(pd.DataFrame(cost_rows),"results/tables/cost_sensitivity.csv",False)
    save(out,"results/timeseries/portfolio_returns.csv")
    save((1+out).cumprod(),"results/timeseries/wealth.csv")
    panel=pd.DataFrame(modules)
    save(panel,"results/timeseries/module_returns.csv")
    module_compare=[]
    switching=[]
    for mode in ["dual","relative","absolute","static"]:
        _,_,_,md2=holdings(prices,mode)
        md2["return_date"]=md2.decision_date+pd.offsets.MonthEnd(1)
        md2=md2[md2.return_date<=prices.index[-1]]
        p2={}
        for m in MODULES:
            mw=md2.loc[md2.module==m].set_index("return_date")[ASSETS]
            mr=(mw*returns.loc[mw.index]).sum(axis=1)
            p2[m]=mr
            module_compare.append({"module":m,"mode":mode,**statistics(mr,asset[CASH])})
            changes=mw.diff().abs().sum(axis=1)>1e-10
            changes.iloc[0]=False
            switching.append({"module":m,"mode":mode,"switches_per_year":changes.sum()*12/len(mw)})
        if mode=="relative": save(pd.DataFrame(p2).corr(),"results/tables/relative_module_correlation.csv")
    save(pd.DataFrame(module_compare),"results/tables/module_comparison.csv",False)
    save(pd.DataFrame(switching),"results/tables/module_switches.csv",False)
    save(pd.DataFrame([{"asset":a,**statistics(asset[a],asset[CASH])} for a in ASSETS]),"results/tables/asset_performance.csv",False)
    common=out[["Dual","Extra month lag"]].dropna()
    save(pd.DataFrame([{"strategy":a,**statistics(common[a],asset[CASH])} for a in common]),"results/tables/lag_common_sample.csv",False)
    metrics=[]
    periods={"Full":(idx[0],idx[-1]),"Overlap to 2011":(idx[0],"2011-12-31"),"Extension 2012+":("2012-01-01",idx[-1]),"Crisis 2008-09":(idx[0],"2009-12-31"),"2020":("2020-01-01","2020-12-31"),"2022":("2022-01-01","2022-12-31"),"2026 H1":("2026-01-01",idx[-1])}
    for period,(a,b) in periods.items():
        for name,r in {**{c:out[c] for c in out},**{c:panel[c] for c in panel}}.items():
            rr=r.loc[a:b].dropna()
            metrics.append({"period":period,"strategy":name,"first":str(rr.index[0].date()),"last":str(rr.index[-1].date()),**statistics(rr,asset[CASH])})
    save(pd.DataFrame(metrics),"results/tables/performance.csv",False)
    save(panel.corr(),"results/tables/module_correlation.csv")
    use=[]
    md=pd.read_csv(ROOT/"results/timeseries/module_holdings.csv")
    for m,pair in MODULES.items():
        for a in pair+[CASH]:use.append({"module":m,"asset":a,"allocation_pct":100*md.loc[md.module==m,a].mean()})
    save(pd.DataFrame(use),"results/tables/utilization.csv",False)
    examples=pd.concat([weights["Dual"].head(1),weights["Dual"].loc["2008-10-31":"2008-10-31"],weights["Dual"].loc["2020-03-31":"2020-03-31"],weights["Dual"].loc["2022-06-30":"2022-06-30"],weights["Dual"].tail(1)])
    save(examples,"results/tables/representative_holdings.csv")
    lit=pd.DataFrame([("Equities",15.79,12.77,.73,-23.01), ("Credit",10.49,4.74,.97,-8.20),("REITs",16.78,13.24,.77,-23.74),("Stress",16.65,17.04,.59,-24.78),("Dual",14.93,7.99,1.07,-10.92)],columns=["strategy","annual_return_pct","volatility_pct","sharpe","max_drawdown_pct"])
    save(lit,"results/tables/paper_table10.csv",False)
    sub=out.loc["2012-01-01":,["Dual","Static","Buffer","Cash"]].to_numpy()
    rng=np.random.default_rng(9339)
    diffs=[]
    for _ in range(2000):
        starts=rng.integers(0,len(sub),size=int(np.ceil(len(sub)/12)))
        inds=np.concatenate([(s+np.arange(12))%len(sub) for s in starts])[:len(sub)]
        x=sub[inds];ex=x[:,:3]-x[:,3,None]
        sr=ex.mean(axis=0)/ex.std(axis=0,ddof=1)*np.sqrt(12)
        diffs.append([sr[0]-sr[1],sr[2]-sr[0]])
    ci=[]
    for j,name in enumerate(["Dual minus Static","Buffer minus Dual"]):
        lo,hi=np.quantile(np.asarray(diffs)[:,j],[.025,.975])
        ci.append({"comparison":name,"lower95":lo,"upper95":hi,"replications":2000,"block_months":12,"seed":9339})
    save(pd.DataFrame(ci),"results/tables/bootstrap.csv",False)
    plt.rcParams.update({"font.family":"serif","font.size":9,"axes.spines.top":False,"axes.spines.right":False,"figure.dpi":160,"savefig.bbox":"tight"})
    colors=["#174963","#b35b32","#54775b","#946d9a","#777777"]
    def finish(fig,name):
        fig.tight_layout();fig.savefig(ROOT/f"results/figures/{name}.pdf");plt.close(fig)
    fig,ax=plt.subplots(2,1,figsize=(7,6),sharex=True)
    for c,col in zip(["Dual","Relative","Static","US equities","Cash"],colors):
        w=(1+out[c]).cumprod(); ax[0].plot(w,label=c,color=col,lw=1.1);ax[1].plot(100*(w/w.cummax().clip(lower=1)-1),color=col,lw=.9)
    ax[0].set_yscale("log");ax[0].set_ylabel("Growth of $1 (log scale)");ax[0].legend(ncol=3,fontsize=8);ax[1].set_ylabel("Drawdown (%)");finish(fig,"composite")
    fig,axes=plt.subplots(2,2,figsize=(7,5),sharex=True)
    for ax,(m,pair) in zip(axes.flat,MODULES.items()):
        for a,col in zip(pair,colors[1:3]): ax.plot((1+asset[a]).cumprod(),label=a,color=col,lw=.8)
        ax.plot((1+panel[m]).cumprod(),label="Dual",color=colors[0],lw=1.2);ax.set_title(m);ax.set_yscale("log");ax.legend(fontsize=7);ax.xaxis.set_major_locator(mdates.YearLocator(5));ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    finish(fig,"modules")
    fig,ax=plt.subplots(2,1,figsize=(7,5),sharex=True)
    ax[0].stackplot(weights["Dual"].index,weights["Dual"].to_numpy().T,labels=ASSETS,colors=plt.get_cmap("tab20").colors[:9],linewidth=0)
    ax[0].set_ylabel("Portfolio weight");ax[0].legend(ncol=5,fontsize=7,loc="upper left")
    ax[1].plot(1-weights["Dual"][CASH],color=colors[0]);ax[1].set_ylabel("Risky allocation");ax[1].set_ylim(0,1.05);finish(fig,"allocations")
    fig,ax=plt.subplots(1,2,figsize=(7,3))
    for c,col in zip(["Dual","Relative","Static"],colors):
        x=100*out[c].sort_values().to_numpy();ax[0].plot(x,np.arange(1,len(x)+1)/len(x),label=c,color=col)
    ax[0].set_xlabel("Monthly return (%)");ax[0].set_ylabel("Empirical probability");ax[0].legend(fontsize=7)
    ax[1].boxplot([100*out[c] for c in ["Dual","Relative","Static","Buffer"]],tick_labels=["Dual","Relative","Static","Buffer"],showfliers=True);ax[1].set_ylabel("Monthly return (%)");finish(fig,"distributions")
    fig,ax=plt.subplots(2,1,figsize=(7,5),sharex=True)
    for c,col in zip(["Dual","Buffer"],colors):ax[0].plot((1+out[c]).cumprod(),label=c,color=col)
    ax[0].legend();ax[0].set_ylabel("Growth of $1")
    for c,col in zip(["Dual","Buffer"],colors):ax[1].plot(trades[c].rolling(12).sum(),label=c,color=col)
    ax[1].set_ylabel("12-month dollars traded / NAV");finish(fig,"buffer")
    summary={"first_return":str(idx[0].date()),"last_return":str(idx[-1].date()),"months":len(idx),"average_risky_allocation_pct":100*risk,"inputs_unchanged":True,"full_2000_2009_available":False,"end_of_month_execution":"Frictionless boundary convention; an extra month of lag is reported separately."}
    (ROOT/"results/summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    pkgs=["numpy","pandas","scipy","matplotlib","requests","pypdf","pytest"]
    (ROOT/"requirements-lock.txt").write_text("# Versions recorded in the shared course environment; do not uv sync.\n"+"\n".join(f"{p}=={importlib.metadata.version(p)}" for p in pkgs)+"\n")
    print(json.dumps(summary,indent=2)); print(pd.DataFrame(metrics).query("period == 'Full'")[["strategy","cagr_pct","sharpe","max_drawdown_pct"]].to_string(index=False))
if __name__=="__main__":main()
