import hashlib, json
import pandas as pd
from .config import ROOT, ASSETS, END

def load():
    manifest = json.loads((ROOT/"data/manifest.json").read_text())
    for name, meta in manifest["files"].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != meta["sha256"]:
            raise ValueError(f"Input changed: {name}")
    frames, quality = [], []
    for a in ASSETS:
        j = json.loads((ROOT/"data/raw"/f"{a}.json").read_text())["chart"]["result"][0]
        dates = pd.to_datetime(j["timestamp"],unit="s",utc=True).tz_convert("America/New_York").tz_localize(None).normalize()
        s = pd.Series(j["indicators"]["adjclose"][0]["adjclose"],index=dates,name=a).loc[:END]
        if s.index.has_duplicates or not s.index.is_monotonic_increasing or (s.dropna()<=0).any(): raise ValueError(a)
        frames.append(s)
        quality.append({"asset":a,"first":str(s.first_valid_index().date()),"last":str(s.last_valid_index().date()),"rows":len(s),"missing_values":int(s.isna().sum()),"dividend_events":len(j.get("events",{}).get("dividends",{})),"split_events":len(j.get("events",{}).get("splits",{}))})
    daily = pd.concat(frames,axis=1)
    for q in quality:
        q["missing_vs_us_sessions_after_inception"] = int(daily.loc[q["first"]:END,q["asset"]].isna().sum())
    # Select the actual last common US session in each calendar month, never an earlier stale quote.
    dates = daily.groupby(daily.index.to_period("M")).apply(lambda x:x.index[-1])
    monthly = daily.loc[dates.to_numpy()].copy()
    monthly.index = monthly.index.to_period("M").to_timestamp("M")
    common = monthly.dropna()
    expected = pd.date_range(common.index[0],END,freq="ME")
    if not common.index.equals(expected): raise ValueError("An internal month is missing; do not silently bridge it")
    if any(q["missing_values"] or q["missing_vs_us_sessions_after_inception"] for q in quality): raise ValueError("Inspect missing daily data before proceeding")
    return daily, common, pd.DataFrame(quality)
