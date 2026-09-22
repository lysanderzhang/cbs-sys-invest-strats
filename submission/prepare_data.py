"""Read frozen baseline and supplied workbook for one Excel submission package.

This is a read-only staging step. Workbook authoring is done by build_submission.mjs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "outputs" / "baseline"
VAL = ROOT / "outputs" / "validation"
OUT = ROOT / "submission" / "submission_data.json"


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.to_json(orient="records", date_format="iso", date_unit="s"))


manifest = json.loads((BASE / "run_manifest.json").read_text())
source = Path(manifest["input_path"])
actual_hash = hashlib.sha256(source.read_bytes()).hexdigest()
assert actual_hash == manifest["input_sha256"], "Source workbook changed after baseline run"

raw = pd.read_excel(source, sheet_name="AV.Clean")
raw.insert(0, "source_excel_row", range(2, len(raw) + 2))
raw_daily = pd.read_excel(source, sheet_name="BBRG.Daily")
raw_daily.insert(0, "source_excel_row", range(2, len(raw_daily) + 2))
raw_intraday = pd.read_excel(source, sheet_name="BBRG.Intraday")
raw_intraday.insert(0, "source_excel_row", range(2, len(raw_intraday) + 2))

data = {
    "manifest": manifest,
    "source_sha256": actual_hash,
    "raw": records(raw),
    "raw_daily": records(raw_daily),
    "raw_intraday": records(raw_intraday),
    "features": records(pd.read_csv(BASE / "features.csv")),
    "daily_inputs": records(pd.read_csv(BASE / "daily_inputs.csv")),
    "performance": records(pd.read_csv(BASE / "performance.csv").rename(columns={"Unnamed: 0": "model"})),
    "sensitivity": records(pd.read_csv(VAL / "sensitivity_summary.csv")),
    "concentration": records(pd.read_csv(VAL / "C_concentration.csv")),
    "ranked_days": records(pd.read_csv(VAL / "C_ranked_days.csv")),
    "noise_april": records(pd.read_csv(VAL / "april02_1130_noise_14.csv")),
    "vol_april": records(pd.read_csv(VAL / "april02_volatility_14.csv")),
}
for model in "ABC":
    data[f"{model}_daily"] = records(pd.read_csv(BASE / f"{model}_daily.csv"))
    data[f"{model}_trades"] = records(pd.read_csv(BASE / f"{model}_trades.csv"))
    data[f"{model}_executions"] = records(pd.read_csv(BASE / f"{model}_executions.csv"))
data["SPY_gross_daily"] = records(pd.read_csv(BASE / "SPY_gross_daily.csv"))

OUT.write_text(json.dumps(data, allow_nan=False, separators=(",", ":")))
print(json.dumps({k: len(v) for k, v in data.items() if isinstance(v, list)}, indent=2))
