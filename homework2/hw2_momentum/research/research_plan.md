# Frozen research plan

Frozen before downloading data or examining any strategy performance. Exact timestamp and SHA256 are in freeze.json. User cutoff: September 30, 2026; evaluate only complete months supported by the actual files. No WRDS, new data charges, trading, publishing, or submission.

## Hypotheses

A1: trailing volatility sizing may lower realized risk versus static Mom exposure.
A2: de-risking after negative 24-month market returns and elevated VIX may lower downside losses, while missing rebounds and sacrificing returns.
B1: relative selection may outperform equal weighting on some return/risk measures.
B2: an absolute cash hurdle may reduce prolonged decline exposure but incur whipsaw and opportunity costs.
B3: an unlevered volatility cap may stabilize risk but lower upside participation.

## Fixed primary design

config/base.yaml records all defaults. A0/A1/A2/A3 use daily French Mom and cash-plus-factor capital, on a common VIX/warmup sample. Official monthly Mom remains separate. B0/B1/B2/B3, SPY buy/hold, monthly 60/40 SPY/IEF and cash use identical primary dates after B3's additional 126-day B2 warmup. Generate B2 warmup before the common test; reset all primary portfolios from cash at the first common execution to include initial costs fairly. B3's forecast uses the gross historical B2 excess return path, so assumed trading costs do not change its risk signal. This resolves the unspecified gross/net sizing convention prospectively.

Snapshot penultimate session close, execution final session close, old holdings earn execution-day returns. Twelve-month signals compare monthly snapshots; skip sensitivity uses snapshots t-1 versus t-13 (12 months ending one month earlier). Costs use a pre-cost NAV turnover charge followed by post-cost target allocation, the permitted proportional haircut approximation. Cash earns daily French RF. No dividend double counting, leverage in B, or daily rebalance.

## Evaluation and uncertainty

Development through 2013; validation 2014-2019; historical holdout 2020 to available complete endpoint. Retain rolling histories at boundaries. This holdout is historical and publicly known, not pristine unseen evidence. No rule changes after performance inspection; any bug correction and rerun is logged. Metrics: daily NAV/drawdown, monthly cash-adjusted Sharpe and Sortino (sqrt(12)*mean excess / sqrt(mean(min(excess,0)^2))), CAGR on elapsed ACT/365.25 including initial execution day, sample skew/excess kurtosis, worst month/three-month path, empirical 95% loss VaR/ES, cash/exposure, turnover/costs, CAPM and contextual HAC(3) regressions. Full precision CSVs and five-decimal report tables. Six-month paired moving-block bootstrap, 1000 replications, seed 9339; differences in annualized mean excess and monthly Sharpe. Report uncertainty for components versus their parent and benchmarks; no independent-month assumption.

## Predetermined sensitivities

A combined: windows 63/252 versus 126; targets .08/.12 versus .10; VIX 20/30 versus 25; bear horizons 12/36 versus 24; cap 1 versus 1.5. Recompute eligibility; compare all these on their longest common warmup window. Exposure-change cost sensitivities 10/25 bps on 2*abs(delta a), and annual drag 1%/2% on exposure; explicitly incomplete. Long-history A0/A1, without VIX, separately common dates.
B2 and B3: lookback 6/9; K 2/4; skip one month; costs 0/5/25/50 bps; remove each ticker once; execute one trading day later using the same frozen snapshot. All are one-at-a-time; primary stays unchanged. B sensitivities compare on primary common dates with full signal history. Record all variant results and dates.
Stress windows: A 2008-2009, March-May 2009, 2020 and mechanically worst months; B 2020, 2022 and mechanically worst months. Never exclude crises from headline history. Capacity: evolving initial 1m/10m/50m NAV, lagged raw close*volume ADV20 at signal; p95/max by ticker and illustrative 1%/5% thresholds, not guaranteed capacity.

## Selection order

Data/accounting reliability; executable objective and clarity; matched-date modeled net performance/downside/exposure; chronological/sensitivity stability; cost/liquidity assumptions; defensible advantage. Prefer simpler B2 if comparable to B3. Weak evidence yields a research-stage ETF pitch rather than a promised advantage or a switch to a high-Sharpe uninvestable factor experiment.
