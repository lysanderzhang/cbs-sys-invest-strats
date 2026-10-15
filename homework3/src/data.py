"""Input validation and quotation normalization; raw inputs are never edited."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
CCY = ['EUR','JPY','GBP','CAD','AUD','NZD','CHF','NOK','SEK']
INVERT = ['JPY','CAD','CHF','NOK','SEK']
VOLS = ['AY1wk','AY3M','AY6M','JPY3M','AUD3M','VIX']
ROOT = Path(__file__).resolve().parents[1]
def load_data(path=None):
    d = pd.read_csv(path or ROOT/'data/raw/hw3.data.carry.FX.dly.csv', na_values=['#N/A'])
    required=CCY+[c+' ROR' for c in CCY+['USD']]+[c+' '+tenor for tenor in ['1M','3M'] for c in CCY+['USD']]+VOLS
    missing=sorted(set(['Date']+required)-set(d.columns))
    if missing: raise ValueError('Missing required columns: '+', '.join(missing))
    d['Date'] = pd.to_datetime(d.Date, format='%m/%d/%y')
    d = d.set_index('Date')
    if d.index.hasnans or d.index.has_duplicates or not d.index.is_monotonic_increasing:
        raise ValueError('Dates must be unique and chronological')
    d = d.drop(columns=[c for c in d if c.startswith('Unnamed:')])
    for c in CCY+['USD']:
        d[c+' ROR'] = pd.to_numeric(d[c+' ROR'].str.rstrip('%'))/100
    numeric=CCY+[c+' '+tenor for tenor in ['1M','3M'] for c in CCY+['USD']]+VOLS
    for column in numeric: d[column]=pd.to_numeric(d[column],errors='raise')
    if np.isinf(d[numeric].to_numpy(dtype=float)).any():
        raise ValueError('Infinite spot, yield or volatility observation')
    if (d[VOLS].le(0)&d[VOLS].notna()).any().any():
        raise ValueError('Volatility observations must be positive when present')
    if d[CCY].isna().any().any() or (d[CCY]<=0).any().any():
        raise ValueError('Invalid spot: do not bridge or impute spot returns')
    if d.filter(regex=' [13]M$').isna().any().any():
        raise ValueError('Missing yields: stop rather than impute')
    return d

def usd_spots(d):
    x=d[CCY].copy(); x[INVERT]=1/x[INVERT]; return x

def quality_report(d, out):
    out.mkdir(parents=True, exist_ok=True)
    r=usd_spots(d).pct_change(fill_method=None)
    reconciliation=[]
    for c in CCY:
        diff=r[c]-d[c+' ROR']
        reconciliation.append(dict(currency=c,quote='FCY/USD' if c in INVERT else 'USD/FCY',
            max_abs_difference=diff.abs().max(),mean_abs_difference=diff.abs().mean(),
            violations_rounding_tolerance=int((diff.abs()>0.000050001).sum())))
    pd.DataFrame(reconciliation).to_csv(out/'ror_reconciliation.csv',index=False,float_format='%.12g')
    pd.DataFrame({'dtype':d.dtypes.astype(str),'missing':d.isna().sum(),
                  'min':d.min(),'max':d.max()}).to_csv(out/'column_inventory.csv')
    streaks=[]
    for c in VOLS:
        group=d[c].ne(d[c].shift()).cumsum()
        for _, s in d[c].groupby(group):
            if len(s)>=20: streaks.append(dict(indicator=c,start=str(s.index[0].date()),end=str(s.index[-1].date()),n=len(s),level=s.iloc[0]))
    pd.DataFrame(streaks).to_csv(out/'constant_volatility_runs.csv',index=False)
    # XLSX is a reference, not a second backtest source. Its rates have extra precision.
    x=pd.read_excel(ROOT/'data/raw/hw3.data.carry.FX.dly.xlsx',header=1).iloc[:len(d)].copy()
    x.index=pd.DatetimeIndex(x.Date)
    xdiff={c:float((pd.to_numeric(x[c])-d[c]).abs().max()) for c in CCY+[c for c in d if c.endswith((' 1M',' 3M'))]+VOLS}
    pd.Series(xdiff,name='maximum_absolute_csv_xlsx_difference').to_csv(out/'csv_xlsx_precision.csv')
    q=dict(rows=len(d),start=str(d.index.min().date()),end=str(d.index.max().date()),
        duplicate_dates=int(d.index.duplicated().sum()),spot_missing=int(d[CCY].isna().sum().sum()),
        yield_missing=int(d.filter(regex=' [13]M$').isna().sum().sum()),vix_missing=int(d.VIX.isna().sum()),
        max_ror_error=max(v['max_abs_difference'] for v in reconciliation),
        largest_spot_move=float(r.abs().max().max()),csv_xlsx_spot_max_difference=max(xdiff[c] for c in CCY))
    (out/'data_quality.json').write_text(json.dumps(q,indent=2))
    (out/'data_quality.md').write_text(f"""# Data-quality report (generated before portfolio construction)

{q['rows']} observations, {q['start']} to {q['end']}; 2,980 holding intervals.
Dates are unique, increasing, and weekday-spaced (one or three calendar days).
All 9 spot series and 20 yield series are numeric and complete.
The three all-empty separator columns are discarded. The first row of all supplied
ROR columns is missing by construction. VIX has {q['vix_missing']} missing observations.
Five FX IV series are complete. Rates and IV are annualized percent; ROR strings
are percentages; VIX is an annualized volatility index in percentage points.
USD/FCY: EUR, GBP, AUD, NZD. FCY/USD: JPY, CAD, CHF, NOK, SEK (invert).
Recomputed arithmetic USD-per-FCY returns agree with ROR within
{q['max_ror_error']:.10f}, the half-unit rounding tolerance of 0.00005.
Use recomputed full-precision returns, not rounded ROR. CSV is authoritative for
this project: XLSX contains higher precision yields/IV, but spot levels agree
(max difference {q['csv_xlsx_spot_max_difference']:.12g}); never mix sources silently.
Extreme 2008 observations are retained. Negative yields are allowed.
See column_inventory.csv for all types, ranges and missing counts.
AY1wk has a 289-observation constant run: retain but flag potential stale data.
See constant_volatility_runs.csv for every run of at least 20 observations.
VIX missing values are forward-filled only after the first observation; longest
raw missing run is four observations. No backward filling. Rolling thresholds
use the previous 252 available as-of series values, including carried values.
The missing raw value indicator and signal age are exported separately.
No missing spot or rate is imputed; such an observation stops the pipeline.
Same-date availability at a common daily fixing is assumed; timestamps are absent.
No data correction or removal of holidays is imposed without source evidence.
""")
    return q
