from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MODULES = {"Equities": ["VTI", "EFA"], "Credit": ["HYG", "LQD"], "REITs": ["VNQ", "REM"], "Stress": ["GLD", "TLT"]}
CASH = "SHV"
ASSETS = [a for pair in MODULES.values() for a in pair] + [CASH]
END = "2026-06-30"
