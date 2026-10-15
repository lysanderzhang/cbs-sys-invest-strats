# Data-quality report (generated before portfolio construction)

2981 observations, 1999-01-01 to 2010-06-04; 2,980 holding intervals.
Dates are unique, increasing, and weekday-spaced (one or three calendar days).
All 9 spot series and 20 yield series are numeric and complete.
The three all-empty separator columns are discarded. The first row of all supplied
ROR columns is missing by construction. VIX has 108 missing observations.
Five FX IV series are complete. Rates and IV are annualized percent; ROR strings
are percentages; VIX is an annualized volatility index in percentage points.
USD/FCY: EUR, GBP, AUD, NZD. FCY/USD: JPY, CAD, CHF, NOK, SEK (invert).
Recomputed arithmetic USD-per-FCY returns agree with ROR within
0.0000500000, the half-unit rounding tolerance of 0.00005.
Use recomputed full-precision returns, not rounded ROR. CSV is authoritative for
this project: XLSX contains higher precision yields/IV, but spot levels agree
(max difference 1.7763568394e-15); never mix sources silently.
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
