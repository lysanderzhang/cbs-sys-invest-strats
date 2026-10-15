from pathlib import Path
import io, re, zipfile, hashlib, json, datetime, inspect
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
URLS = {
 'mom_daily': 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip',
 'mom_monthly': 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_CSV.zip',
 'ff_daily': 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip',
 'ff_monthly': 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip',
 'vix': 'https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv',
}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def parse_french(payload, daily):
    if payload[:2] == b'PK':
        z = zipfile.ZipFile(io.BytesIO(payload))
        names = z.namelist()
        payload = z.read(next(x for x in names if x.lower().endswith('.csv')))
    txt = payload.decode('utf-8-sig')
    n = 8 if daily else 6
    rows, header = [], None
    for line in txt.splitlines():
        cells = [x.strip() for x in line.split(',')]
        if re.fullmatch(r'\d{' + str(n) + r'}', cells[0]):
            rows.append(cells)
        elif cells[0] == '' and any(x in ('Mom','Mkt-RF') for x in cells):
            header = cells[1:]
    if not rows or not header: raise ValueError('No recognized French block')
    df = pd.DataFrame([r[1:] for r in rows], columns=header).apply(pd.to_numeric)
    df = df.replace([-99.99, -999.0, -999.99], float('nan')) / 100
    df.index = pd.to_datetime([r[0] for r in rows], format='%Y%m%d' if daily else '%Y%m')
    if not daily: df.index = df.index + pd.offsets.MonthEnd(0)
    df.index.name = 'date'
    if df.index.has_duplicates: raise ValueError('Duplicate French dates')
    return df.sort_index(), txt[:3000]

def fetch(config):
    manifest = []
    for name,url in URLS.items():
        p = ROOT/'data/raw'/ (name + ('.csv' if name=='vix' else '.zip'))
        if not p.exists():
            errors=[]
            for attempt in range(2):
                try:
                    r=requests.get(url, timeout=45); r.raise_for_status()
                    if len(r.content)<100: raise ValueError('Empty payload')
                    p.write_bytes(r.content); break
                except Exception as e: errors.append(str(e))
            if not p.exists():
                manifest.append({'dataset':name,'status':'BLOCKED','errors':errors}); continue
        if name=='vix':
            df=pd.read_csv(p); df.columns=df.columns.str.strip()
            df['date']=pd.to_datetime(df['DATE']); df=df.set_index('date')[['CLOSE']].rename(columns={'CLOSE':'VIX'})
            header='Cboe VIX closing index points; official historical file'
        else: df,header=parse_french(p.read_bytes(),'daily' in name)
        df=df.loc[:config['data_cutoff']]
        df.to_csv(ROOT/'data/processed'/f'{name}.csv')
        (ROOT/'data/manifests'/f'{name}_header.txt').write_text(header)
        manifest.append({'dataset':name,'status':'OK','url':url,'raw_file':str(p.relative_to(ROOT)), 'sha256':sha(p),'acquired_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),'start':str(df.index.min().date()),'end':str(df.index.max().date()),'rows':len(df),'original_units':'index points' if name=='vix' else 'percent return','normalized_units':'index points' if name=='vix' else 'decimal return','missing':int(df.isna().sum().sum()),'vintage':'current downloaded snapshot; historical revisions possible; French CIZ era since January 2025'})
    import yfinance as yf
    yf.set_tz_cache_location(str(ROOT/'build/yfinance-cache'))
    (ROOT/'data/manifests/yfinance_api.txt').write_text(str(inspect.signature(yf.download))+'\n'+str(inspect.signature(yf.Ticker.history))+'\nversion='+yf.__version__)
    for ticker in config['etf']['tickers']:
        p=ROOT/'data/raw'/f'yahoo_{ticker}.csv'
        opts=dict(start='1990-01-01',end='2026-10-01',interval='1d',auto_adjust=False,back_adjust=False,actions=True,repair=False,keepna=True,rounding=False,prepost=False)
        if not p.exists():
            errors=[]
            for attempt in range(2):
                try:
                    df=yf.Ticker(ticker).history(**opts)
                    if df.empty or 'Adj Close' not in df or df['Adj Close'].notna().sum()<250: raise ValueError('Empty/partial or missing Adj Close')
                    df.index=df.index.tz_localize(None).normalize() if df.index.tz else df.index.normalize()
                    df.index.name='date'; df.loc[:config['data_cutoff']].to_csv(p); break
                except Exception as e: errors.append(str(e))
            if not p.exists():
                manifest.append({'dataset':ticker,'status':'BLOCKED','errors':errors,'adapter':'yfinance','version':yf.__version__,'request':opts});continue
        df=pd.read_csv(p,index_col=0,parse_dates=True)
        manifest.append({'dataset':ticker,'status':'OK','provider':'Yahoo Finance','url':f'https://finance.yahoo.com/quote/{ticker}/history/','raw_file':str(p.relative_to(ROOT)),'sha256':sha(p),'acquired_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),'adapter':'yfinance','version':yf.__version__,'request':opts,'start':str(df.index.min().date()),'end':str(df.index.max().date()),'rows':len(df),'original_units':'USD prices; shares volume; cash distributions USD/share','adjustments':'Adj Close Yahoo distribution/split-adjusted; no dividends added to returns; raw Close/Volume retained as provider reports','missing':int(df.isna().sum().sum())})
    (ROOT/'data/manifests/inputs.json').write_text(json.dumps(manifest,indent=2))
    print(pd.DataFrame(manifest).reindex(columns=['dataset','status','start','end','rows']).to_string(index=False))

def import_csv(ticker,path,provider):
    """Fallback: date, Close, Adj Close, Volume; optional Dividends, Stock Splits."""
    df=pd.read_csv(path,index_col='date',parse_dates=True)
    if not {'Close','Adj Close','Volume'}.issubset(df): raise ValueError('Required fields absent')
    if df.index.has_duplicates: raise ValueError('Duplicate dates')
    dest=ROOT/'data/raw'/f'yahoo_{ticker}.csv'
    if dest.exists(): raise FileExistsError('Preserve original snapshot; use a new project/vintage')
    df.to_csv(dest)
    (ROOT/'data/manifests'/f'{ticker}_import.json').write_text(json.dumps({'provider':provider,'source':str(path),'sha256':sha(dest),'warning':'Requires adjustment, session, volume verification before use'},indent=2))
