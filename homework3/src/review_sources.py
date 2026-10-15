"""Unoptimized cross-file precision check using the supplied higher-precision XLSX."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from .review import moments,histories,CC,VV
ROOT=Path(__file__).resolve().parents[1]

def main():
    csv=pd.read_csv(ROOT/'data/raw/hw3.data.carry.FX.dly.csv');xlsx=pd.read_excel(ROOT/'data/raw/hw3.data.carry.FX.dly.xlsx',header=1)
    dates=pd.DatetimeIndex(pd.to_datetime(csv.Date,format='%m/%d/%y'));assert dates.equals(pd.DatetimeIndex(xlsx.Date))
    spot=csv[CC].to_numpy(float)
    for j,c in enumerate(CC):
        if c in ['JPY','CAD','CHF','NOK','SEK']:spot[:,j]=1/spot[:,j]
    ratio=spot[1:]/spot[:-1];days=np.array([(dates[i]-dates[i-1]).days/365 for i in range(1,len(dates))])
    series={};weights={};rows=[]
    for source,frame in [('CSV',csv),('XLSX',xlsx)]:
        for tenor in ['1M','3M']:
            y=frame[[c+' '+tenor for c in CC]].to_numpy(float)/100
            u=frame['USD '+tenor].to_numpy(float)/100
            excess=np.exp(y[:-1]*days[:,None])*ratio-np.exp(u[:-1]*days)[:,None]
            for k in [2,3]:
                for method in ['equal','rank','spread']:
                    name=f'{tenor}_{k}_{method}';w=np.zeros_like(y)
                    for t in range(len(frame)):
                        order=sorted(range(9),key=lambda j:(-y[t,j],CC[j]));center=sorted(y[t])[4]
                        for ix,sign in [(order[:k],1),(order[-k:][::-1],-1)]:
                            a=np.ones(k) if method=='equal' else (np.arange(k,0,-1,dtype=float) if method=='rank' else sign*(y[t,ix]-center))
                            if sum(a)==0:a=np.ones(k)
                            w[t,ix]=sign*a/sum(a)
                    weights[source,name]=w;series[source,name]=np.sum(w[:-1]*excess,axis=1)
    for name in [name for source,name in series if source=='CSV']:
        a=moments(series['CSV',name]);b=moments(series['XLSX',name]);w0=weights['CSV',name];w1=weights['XLSX',name]
        rows.append(dict(strategy=name,csv_sharpe=a['sharpe'],xlsx_sharpe=b['sharpe'],csv_geometric=a['geometric'],xlsx_geometric=b['geometric'],
            changed_selected_currency_dates=int(np.sum(np.any(np.sign(w0[:-1])!=np.sign(w1[:-1]),axis=1))),
            changed_weight_dates=int(np.sum(np.any(np.abs(w0[:-1]-w1[:-1])>1e-10,axis=1)))))
    out=ROOT/'results/audit';pd.DataFrame(rows).set_index('strategy').to_csv(out/'source_precision.csv',float_format='%.12g')
    winners={s:max([name for ss,name in series if ss==s],key=lambda name:moments(series[s,name])['sharpe']) for s in ['CSV','XLSX']}
    # Keep the original selected baseline fixed to isolate source precision in the volatility filter.
    names={};held={};n=len(csv)
    for source,frame in [('CSV',csv),('XLSX',xlsx)]:
        br=np.r_[np.nan,series[source,'3M_3_equal']]
        for v in VV:
            raw=pd.to_numeric(frame[v],errors='coerce').to_numpy(float);_,_,z,_=histories(raw)
            e=np.r_[np.nan,z[:-1]];held[source,v]=e;names[source+'_'+v]=br*e
    f=pd.DataFrame(names,index=dates).dropna();filters=[]
    for v in VV:
        c=moments(f['CSV_'+v]);x=moments(f['XLSX_'+v])
        filters.append(dict(indicator=v,csv_sharpe=c['sharpe'],xlsx_sharpe=x['sharpe'],
            different_signal_dates=int(np.sum(held['CSV',v][np.isin(dates,f.index)]!=held['XLSX',v][np.isin(dates,f.index)]))))
    pd.DataFrame(filters).set_index('indicator').to_csv(out/'source_precision_filters.csv',float_format='%.12g')
    (out/'source_precision_summary.json').write_text(json.dumps(dict(baseline_winners=winners,fixed_baseline='3M_3_equal',filter_winners={s:max(VV,key=lambda v:moments(f[s+'_'+v])['sharpe']) for s in ['CSV','XLSX']},common_filter_dates=len(f)),indent=2)+'\n')
    print(pd.DataFrame(rows).to_string(index=False));print(json.loads((out/'source_precision_summary.json').read_text()))

if __name__=='__main__':main()
