# First implementation results and independent-verification plan

These are results of a **data-constrained approximation**, not an exact replication of the paper. The unknown timestamp semantics and missing market open are more consequential than small numerical precision differences. All author-code comparisons, execution/VWAP sensitivity studies and parameter optimization remain unperformed at this requested stopping point.

## Implemented specification

A uses the previous 14 sessions' mean absolute time-of-day move from the open proxy, gap-adjusted boundaries, half-hour decisions, opposite-band reversals and session-close liquidation. B changes the exit to max(current upper band, approximate VWAP) for longs and min(current lower band, approximate VWAP) for shorts. C adds the paper's 2% target divided by prior-14-day sample daily SPY volatility, capped at 4 in its sizing formula. Initial capital is $100,000 per model; floor-rounded share counts are fixed within a session. Costs are $0.0035 commission plus $0.001 slippage per share per leg, including closing and reversal legs.

Prices and volumes are made available at the presumed interval end, 30 minutes after their label. The first available price at 10:00 is the open proxy; first possible trading is 10:30. Thus this implementation cannot capture the paper's actual 09:30-to-10:00 move or its 10:00 entry. It also mixes the first half hour into the overnight gap adjustment.

## Common-period results

182 intraday sessions are supplied. The first 14, March 13–April 1, initialize the Noise Area and are not counted as flat scored days. All three models are evaluated on **168 sessions, April 2–December 1, 2025**. The daily sheet provides additional earlier closes for volatility; it cannot provide the missing intraday Noise history.

| Metric | A | B | C | SPY gross |
|---|---:|---:|---:|---:|
| Cumulative return (%) | 3.59421 | 4.47404 | 11.13927 | 21.96250 |
| Annualized geometric return (%) | 5.43948 | 6.78557 | 17.16592 | 34.69128 |
| Annualized volatility (%) | 6.64939 | 7.24061 | 15.49954 | 21.44463 |
| Sharpe, zero risk-free rate | 0.82963 | 0.94237 | 1.09689 | 1.49467 |
| Maximum daily drawdown (%) | -5.05948 | -2.83612 | -4.81698 | -12.05273 |
| Profitable days / all days (%) | 32.14286 | 27.38095 | 27.38095 | 58.92857 |
| Profitable days / nonzero days (%) | 58.69565 | 50.00000 | 50.00000 | 58.92857 |
| Completed round trips | 95 | 135 | 135 | Not comparable |
| Profitable round trips (%) | 58.94737 | 42.96296 | 42.96296 | Not comparable |
| Average net P&L / trade ($) | 37.83382 | 33.14104 | 82.51309 | Not comparable |
| Average net trade return on entry notional (%) | 0.03647 | 0.03304 | 0.03304 | Not comparable |
| Average net trade contribution / day-start equity (%) | 0.03871 | 0.03370 | 0.08396 | Not comparable |
| Average net P&L / share / trade ($) | 0.28516 | 0.19606 | 0.19606 | Not comparable |
| Total costs ($) | 138.33000 | 201.42000 | 534.91500 | 0.00000 |
| Final equity ($) | 103594.21280 | 104474.04100 | 111139.26700 | 121962.50138 |

SPY with one entry and final liquidation cost returns **21.96071%**, ending at $121960.71063. It is a constant fractional-share benchmark bought at the April 1 daily close, so its first scored return is April 2 close-to-close. Strategies begin that session in cash. Both cover the same scored daily return periods; SPY naturally has overnight exposure. Dividend-adjustment metadata is missing, so neither SPY series is advertised as a verified total-return benchmark. The input prices are used as supplied, without an added dividend series.

| Model | Best day | Best return (%) | Worst day | Worst return (%) |
|---|---|---:|---|---:|
| A | 2025-10-10 | 2.32477 | 2025-04-11 | -1.74826 |
| B | 2025-04-09 | 3.73995 | 2025-04-11 | -1.43196 |
| C | 2025-10-10 | 9.32201 | 2025-11-21 | -2.01150 |
| SPY gross | 2025-04-09 | 10.50195 | 2025-04-04 | -5.85428 |

B's realized volatility exceeds A's in this sample, unlike the paper's long-sample result. C's best day is large relative to its total gain. These observations motivate later robustness checks; they are not implementation proof or evidence of stable future performance.

## Regression versus SPY

Estimate daily raw-return OLS: r_strategy = alpha_daily + beta * r_SPY + error, matching the paper's stated regression. Annual alpha is 252*alpha_daily, not a compounded portfolio return. HAC standard errors use five lags; conventional OLS p-values are also saved in `performance.csv`.

| Model | Annual alpha (%) | Beta | Alpha HAC p-value | Beta HAC p-value | 95% annual alpha HAC interval (%) |
|---|---:|---:|---:|---:|---|
| A | 9.82855 | -0.13453 | 0.20912 | 0.00078 | [-5.56154, 25.21865] |
| B | 5.22628 | 0.04983 | 0.47744 | 0.58892 | [-9.26533, 19.71789] |
| C | 17.68759 | -0.02141 | 0.35271 | 0.87931 | [-19.78386, 55.15904] |

No model has statistically significant positive alpha at 5% by these HAC tests. A's estimated negative beta is significant by this specification. With only 168 sessions, episodic large moves, uncertain data construction, and no independent validation, inference is exploratory. HAC errors do not correct measurement error, modeling ambiguity, or selection bias. Do not interpret annualizing this short sample as a forecast. No regression of the benchmark on itself is reported as statistical evidence.

## Complete assumption register

The pre-implementation file gives source-page references and all detected anomalies. The final baseline choices are:

1. New York local timestamps, no timezone metadata; default assumes start-labeled intervals and delays information availability by 30 minutes. This is inferred, not vendor-confirmed.
2. First observed half-hour ending price is the open proxy, known at 10:00. No action at the anchor. This changes both intraday moves and gap measurement.
3. Primary inputs are AV.Clean; raw intraday is for reconciliation. Daily-sheet closes determine lagged close, simple SPY returns, volatility and benchmark. Small closing-price rounding differences are retained and disclosed.
4. Raw volume observations are interval volumes, despite assignment wording. Cumulative volume is constructed by summation; already-cumulative inputs would instead be differenced and validated.
5. Retain only regular-session intervals. Treat the separate 16:00/13:00 print as a liquidation price and exclude its uncertain volume. Do not allocate daily residuals backward or synthesize missing volume.
6. Approximate VWAP is sum(endpoint price*observed interval volume)/sum(observed interval volume), session-reset. Missing tick prices, interval OHLC and dollar turnover prevent exact VWAP. Midpoint weighting is an untested optional alternative.
7. Require 14 preceding trading sessions before scoring. Mean Noise moves use available clock-matched observations in those exact 14 sessions. A known half day reduces later-slot sample count to 13; no stretching to the 15th session or synthetic afternoon prices.
8. Daily volatility uses exactly 14 prior simple close-to-close returns, sample standard deviation ddof=1, shifted one session. Zero volatility uses the leverage cap; missing volatility prevents eligibility. No annualization inside the 2% daily-volatility formula.
9. Begin each model with $100,000. A/B sizing leverage 1; C min(4,.02/sigma). Integer shares are floored using proxy open and prior ending equity, fixed throughout the session. Reentries do not compound intraday realized P&L into new sizing. Insolvency raises an error; zero affordable shares means no trade.
10. Entries use strict price > upper or price < lower levels, not a required fresh crossover. Flat B/C uses the same Noise entry signal as A; no baseline VWAP entry filter. A holds inside the Noise Area. B/C stops use current levels rather than ratcheted historical extrema.
11. Stops use strict inequalities; equality holds existing exposure. Evaluate stops for positions already held at the decision time. If a newly opened position already breaches VWAP, first evaluate its stop at the next decision. There were no such entries in this run, so the entry-filter correction did not change the results.
12. Opposite signals may reverse at the same timestamp, paying an exit and a new entry. A stop exit may not immediately reenter in the same direction at that timestamp. Reentry at a later decision does not require an intervening return to the Noise Area.
13. Signal-time endpoint is the idealized fill reference, with adverse slippage debited separately. No pre-entry interval return is earned. Immediate same-price execution is not verified executable; next-grid execution is provided only as a future sensitivity option. Closing liquidation is pre-scheduled and overrides signals.
14. Scheduled close is 16:00 except 13:00 on the two assignment-specified half days. Never open at close or hold overnight. No intrabar high/low touches, hidden stop fills, partial fills or execution at the boundary are assumed.
15. Charge every one-way share .0035 commission and .001 slippage, constant across size and dates, with no minimum charge or commission tier. Do not also shift fill prices for slippage. No financing/borrow/cash interest/extra fees/market impact are included. These omissions follow the chosen simplified specification, not a claim that such costs are absent in practice.
16. A 4x cap applies to the paper's start-of-day sizing ratio. Actual exposure divided by marked equity is not continuously clamped; price movement and losses can push realized leverage above the sizing cap. Both are logged.
17. No dividend cash flows or new corporate-action corrections are invented. Existing price adjustments cannot be certified; they may affect gaps, volatility, dollars-per-share costs and benchmark interpretation.
18. Score all 168 eligible sessions, including zero-trade days. Common warm-up exclusion, 252-session annualization, sample return standard deviation, zero risk-free rate, and daily-close drawdown including initial capital. Daily drawdown is not worst intraday drawdown.
19. Benchmark uses fractional constant shares; the net version budgets entry costs within initial capital and pays liquidation costs at the last close. No daily benchmark rebalance. Main comparison is the gross supplied-price benchmark, with net results provided separately.
20. A trade means a completed position round trip; reversals complete one trade and start another. Trade hit ratio uses net P&L>0, daily hit ratio uses net daily return>0. Zero results are not wins. Report all-day and nonzero-day denominators separately. Trade returns use both absolute entry notional and day-start equity, clearly named.
21. Regress raw returns with an intercept, not risk-free excess returns; report conventional and HAC(5) uncertainty with 95% intervals. Require at least 30 paired observations and nonzero benchmark variance; do not equate a large point estimate with significant alpha.

Metric formulas: cumulative = E_end/E_initial-1; annualized geometric = (E_end/E_initial)^(252/N)-1; annualized volatility = sd(r,ddof=1)*sqrt(252); Sharpe = mean(r)/sd(r)*sqrt(252); drawdown = min(E_t/max(E_initial,E_1,...,E_t)-1). Gross trade P&L = direction*shares*(exit-entry); net deducts both legs' costs. No external cash flows are assumed.

## Data limitations and unresolved ambiguities

The full column-level audit and seven volume-reconciliation exceptions are in `PRE_IMPLEMENTATION.md`. Key further implications:

- Retained observed interval volumes represent only **67.00805% of daily volume at the median** (range about 46.8963%–79.2906%). Excluded residual volume is substantial. A volume-weighted estimate on observed intervals cannot establish a full-market VWAP. It may also reflect a venue/filter difference, not just absent trades.
- The ending 15:30 prices nearly reproduce the final close, and the 12:30 prices on half days equal the 13:00 close. Start labeling is strongly suggested, but the workbook lacks bar-generation metadata. A timestamp choice cannot be certified from these values alone.
- 09:30 is a label, not an authenticated opening trade. The sample has no daily open/high/low, no bid/ask, trade-level volume, auction identifier, or interval dollar turnover. It cannot settle the market open, exact VWAP, spread, delay/slippage, true intrabar extremes, or fill feasibility.
- Bloomberg's adjusted/unadjusted flags and consolidation filters are unavailable. Preserve this uncertainty even though cleaned/raw prices agree.
- All session dates in the daily sheet are present, and regular-session grids are complete after the chosen half-day handling. This establishes consistency within the supplied workbook, not independent confirmation against an exchange calendar or original Bloomberg feed.
- Neither the paper's half-day historical averaging nor a policy for missing observation slots is specified. Our 13-observation treatment is a visible deviation from the literal 14-observation formula.
- Entry/VWAP interaction, equality, actual-crossing versus level tests, reentry, execution ordering/latency, VWAP inputs, price adjustments, benchmark cost conventions and several performance definitions remain choices rather than author-code-verified facts.
- The main paper, FAQ and appendix summarize different historical endpoints. This 2025 subset cannot be expected to match their published return tables. It cannot support the paper's 17-year regime conclusions or its VIX/gamma/OHLC-pattern studies.
- The baseline .001 slippage assumption is retained. The paper estimates it relative to minute opening prices; 30-minute endpoints cannot verify that experiment or compensate reliably for timing mistakes. No data-forced alternative slippage amount is defensible here.

## Verification performed in this implementation stage

Eight deterministic tests pass: volume-counter rejection/reset handling; a manually calculable VWAP; Noise means using precisely the prior 14-session window including half-day gaps; direct 14-return sample-volatility arithmetic and leverage cap; future-price/volume/daily-close mutation preserving all earlier features and executions; signal/stop/equality rules; a hand-computable reversal with four costs and delayed execution; and full-ledger/session-close checks across A/B/C. Event P&L, completed trades and daily equity reconcile within $0.0000001. Each day's ending position is zero. Both output charts were visually inspected.

These tests establish internal consistency under the selected assumptions. They are not independent strategy verification: the same AI authored both implementation and tests. Timestamp, VWAP and opening-price validity remain unresolved by them.

## Independent verification plan

1. Obtain the Bloomberg export settings or instructor clarification: bar start/end labeling, `Last Price` meaning, regular-session filter, adjustment flags, and origin/timing of AV.Clean residual volume. Get an actual 09:30 opening price and ideally minute OHLCV or trade/dollar-volume data. Keep these checks separate from return-driven choices.
2. On a small fixed selection of days, independently calculate the 14 historical absolute moves, gap bounds, VWAP approximation, lagged volatility, share count, state transitions and both cost legs in a separate spreadsheet or clean-room program. Do not import this module's functions into that verifier.
3. Have another implementation consume the same canonical observations and assumptions. Compare feature rows and first differing trades, not just total returns. Align rounding, price-adjustment, session and cost conventions first.
4. Only in the later authorized validation stage, use the authors' implementation as an independent benchmark. Preserve this delivery and manifest hash before consulting it. Document differences separately as specification versus data versus coding differences.
5. Then test, without optimizing for best performance, true open versus proxy, confirmed timing, endpoint versus midpoint/full VWAP, no-gate versus entry-gate ordering, immediate versus delayed fills, conservative costs, and alternative half-day treatment. Report changes in individual trades as well as totals. Longer out-of-sample data are needed for stronger economic/statistical conclusions.

## Specific spot checks before trusting results

1. Confirm normal-day row 09:30 is first available at 10:00 under this convention and row 15:30 is not used at 15:30. Check `source_timestamp`, `timestamp`, and `price_source_timestamp`; the final field distinguishes the actual closing print from the interval price used in VWAP.
2. For **April 2, 11:30**, calculate all 14 preceding days' 11:30 absolute moves by hand. Expected U=559.54864, L=553.61247, approximate VWAP=557.43009, current price=560.08670. Check the long entry condition.
3. On April 2, check O_proxy=555.38370, previous close=557.76980 and the daily input volatility. C leverage is approximately 1.68193; floor(100000*leverage/555.38370)=302 shares. The current day's return must not enter that volatility.
4. C's first round trip: April 2 11:30 long 302 at 560.08670, exit 12:00 at 559.13220. Gross = -288.25900; total cost = 302*.009 = 2.71800; net = **-290.97700**. Exit follows the current upper-bound stop, not an assumed intrabar fill at the bound.
5. April 2's second C trade nets **-999.65020**, so daily net is **-1290.62720** and equity **98709.37280**. Entry rows carry their own costs; summing exit-event net P&L alone is wrong.
6. On **July 3**, C buys 501 shares at 11:00 for 623.57110 and closes at **13:00** for 623.61100. Gross=19.98990; cost=4.50900; net=**15.48090**. No stale afternoon row should become a decision. **November 28 has no C trade**, which is valid, but its data still stop at 13:00.
7. For **July 7 14:00** and **December 1 14:00**, verify `noise_count=13` within exactly 14 prior sessions. Confirm July 3/November 28 are absent at that clock time and the computation has not substituted a stale afternoon price or reached back one extra session.
8. Inspect March 13's volume overcount and the six undercounted dates. Confirm none is “repaired” by distributing the closing residual into earlier VWAP. Compare the cumulative retained-volume total with the daily volume to appreciate the missing coverage.
9. Hand-check one A reversal: two execution rows at one timestamp, closing old shares then entering opposite shares, with cost on each. The synthetic test has known prices 102 to 98 (long) and 98 to 97 (short), 1,000 shares, four legs: total net **-3018.00000**.
10. Verify C's October 10 gain **9.32201%** and November 21 loss **-2.01150%** from individual trades; inspect marked exposure rather than assuming the sizing cap continuously caps leverage.
11. Rebuild daily P&L independently from signed inventory times successive price changes and separate costs, rather than only the realized trade formula used here. Reconcile terminal equity to **111139.26700** for C.
12. Verify SPY starts from the April 1 closing price, uses the identical 168 scored dates, holds a constant share count, and does not receive fabricated dividends. Check the initial $100,000 point is included in drawdown peaks, and that zero-trade strategy days remain in Sharpe and daily-hit calculations.

Stop here: complete independent validation and sensitivity assessment before treating this first implementation as the assignment's final verified version.
