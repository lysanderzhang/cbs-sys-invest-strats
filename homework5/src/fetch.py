"""Optional online acquisition. Frozen snapshots are used for normal reproduction."""
import argparse, hashlib, json
from datetime import datetime, timezone
import requests
from .config import ROOT, ASSETS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Explicitly replace all snapshots and manifest")
    args = parser.parse_args()
    paths = [ROOT / "data/raw" / f"{a}.json" for a in ASSETS]
    if any(p.exists() for p in paths) and not args.refresh:
        raise SystemExit("Snapshots already exist. Normal reproduction is offline; use --refresh deliberately.")
    manifest = {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "start_requested": "2006-01-01", "end_inclusive": "2026-06-30", "files": {}}
    # UTC bounds include the full final US session; no data after June 30 enter the analysis.
    start = int(datetime(2006,1,1,tzinfo=timezone.utc).timestamp())
    end = int(datetime(2026,7,1,tzinfo=timezone.utc).timestamp())
    pending = []
    for a,p in zip(ASSETS,paths):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{a}"
        response = requests.get(url, params={"period1": start, "period2": end, "interval": "1d", "events": "div,splits"}, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        response.raise_for_status()
        obj = response.json()
        if obj["chart"]["error"]: raise ValueError(obj["chart"]["error"])
        result = obj["chart"]["result"][0]
        if "adjclose" not in result["indicators"]: raise ValueError(f"No adjusted close for {a}")
        raw = response.content
        pending.append((p,raw))
        manifest["files"][str(p.relative_to(ROOT))] = {"url": response.url, "sha256": hashlib.sha256(raw).hexdigest(), "rows": len(result["timestamp"]), "currency": result["meta"]["currency"]}
        print(a,len(result["timestamp"]),flush=True)
    for p,raw in pending: p.write_bytes(raw)
    for p in sorted((ROOT/"references").glob("*.pdf")):
        manifest["files"][str(p.relative_to(ROOT))] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "source": "User-supplied reference"}
    (ROOT/"data/manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
if __name__ == "__main__": main()
