# Independent reconstruction, ambiguity sensitivity, and concentration

The original baseline files and assumptions remain unchanged. This phase reconstructs source observations directly in a separate program without importing or calling `strategy.py`. It uses explicit sums for historical estimates and inventory-times-price-change accounting for equity, rather than the original rolling calculations and realized-trade equity ledger. Only after this replay are frozen baseline CSVs opened for reconciliation.

All 34 reconciliation checks pass. All A/B/C trade episodes match, and the largest numerical difference among checked fields is less than $0.000000001. This is implementation-level corroboration by a second code path, **not blind third-party validation**: the same AI generated it with knowledge of the baseline conventions. It does not validate Bloomberg timestamp semantics, actual opens, true VWAP, or executable fill prices. No author code was consulted.

## Manual reproduction tables

`validation_tables.xlsx` contains formulas, raw source values, exact source sheet/cell addresses, and chronological position/P&L calculations. Read Summary, then Noise/Volatility/VWAP, Decisions and Trades. Daily Equity provides the independently reconstructed beginning capital for every scored session. The separate CSVs expose the same inputs without formatting.

The four requested days have 46 decision rows and six round trips. Supporting tables include 644 historical Noise observations and 56 lagged daily-return observations: all clock-time histories needed for all four days, not just April 2 at 11:30. Availability timestamps are baseline-inferred bar endpoints; all original proxy assumptions are retained.

The workbook is a manual arithmetic model, not a full interactive backtester. Its formulas recalculate raw-price ratios, variance, sizing, VWAP, selected-day state transitions, trade P&L and concentration. Daily Equity's independently replayed gross/cost inputs and sensitivity results are fixed snapshots. Editing a source value locally does not resimulate all future historical trades or re-rank concentration dates. The Python replay is supplied for that purpose.

### April 2: all 14 observations for the 11:30 Noise Area

For each historical session, O is AV.Clean's 09:30-labeled price (the baseline 10:00 open proxy), and P is its 11:00-labeled price (available at 11:30). Calculate m=ABS(P/O-1). Source columns below are literal cells in the original workbook.

| Historical day | Open proxy | 11:30 price | Open cell | Price cell | Absolute move |
| --- | --- | --- | --- | --- | --- |
| 2025-03-13 | 549.94530 | 549.42590 | AV.Clean!B2545 | AV.Clean!B2542 | 0.0009444576 |
| 2025-03-14 | 552.07280 | 556.20680 | AV.Clean!B2531 | AV.Clean!B2528 | 0.0074881429 |
| 2025-03-17 | 560.50390 | 559.15580 | AV.Clean!B2517 | AV.Clean!B2514 | 0.0024051572 |
| 2025-03-18 | 555.88310 | 554.99720 | AV.Clean!B2503 | AV.Clean!B2500 | 0.0015936804 |
| 2025-03-19 | 559.21030 | 559.69600 | AV.Clean!B2489 | AV.Clean!B2486 | 0.0008685462 |
| 2025-03-20 | 561.68850 | 563.96860 | AV.Clean!B2475 | AV.Clean!B2472 | 0.0040593674 |
| 2025-03-21 | 556.73650 | 556.61660 | AV.Clean!B2461 | AV.Clean!B2458 | 0.0002153622 |
| 2025-03-24 | 569.52750 | 570.46710 | AV.Clean!B2447 | AV.Clean!B2444 | 0.0016497886 |
| 2025-03-25 | 571.42660 | 572.41600 | AV.Clean!B2433 | AV.Clean!B2430 | 0.0017314560 |
| 2025-03-26 | 570.25130 | 569.04530 | AV.Clean!B2419 | AV.Clean!B2416 | 0.0021148571 |
| 2025-03-27 | 565.09300 | 566.61920 | AV.Clean!B2405 | AV.Clean!B2402 | 0.0027007944 |
| 2025-03-28 | 559.87790 | 555.70180 | AV.Clean!B2391 | AV.Clean!B2388 | 0.0074589477 |
| 2025-03-31 | 546.58910 | 549.31840 | AV.Clean!B2377 | AV.Clean!B2374 | 0.0049933305 |
| 2025-04-01 | 554.02150 | 557.58110 | AV.Clean!B2363 | AV.Clean!B2360 | 0.0064250214 |

Sum of the 14 absolute moves = 0.044648909605. Divide by 14 to get **0.003189207829**, or 0.31892%.

- Current proxy open: 555.38370 from AV.Clean!B2349.
- Previous daily close: 557.76980 from BBRG.Daily!C170.
- Upper = MAX(555.38370, 557.76980) × (1 + 0.003189207829) = **559.54864**.
- Lower = MIN(555.38370, 557.76980) × (1 − 0.003189207829) = **553.61247**.
- At 11:30, price 560.08670 exceeds upper 559.54864, so a flat Model C enters long.

### April 2: all 14 lagged daily returns

Each simple return is closing price / previous closing price − 1. The source rows run from the March 12 prerequisite close through the April 1 close; the first return is March 13, and April 2's return is excluded. Squared deviations below use the full-precision mean, not a rounded displayed mean.

| Return date | Previous close | Close | Prior source | Close source | Return | Squared deviation |
| --- | --- | --- | --- | --- | --- | --- |
| 2025-03-13 | 554.01580 | 546.63050 | BBRG.Daily!C184 | BBRG.Daily!C183 | -0.0133304862 | 0.000192615184 |
| 2025-03-14 | 546.63050 | 557.92160 | BBRG.Daily!C183 | BBRG.Daily!C182 | 0.0206558178 | 0.000404320274 |
| 2025-03-17 | 557.92160 | 562.22390 | BBRG.Daily!C182 | BBRG.Daily!C181 | 0.0077112985 | 0.000051311399 |
| 2025-03-18 | 562.22390 | 556.14710 | BBRG.Daily!C181 | BBRG.Daily!C180 | -0.0108085053 | 0.000128972506 |
| 2025-03-19 | 556.14710 | 562.20400 | BBRG.Daily!C180 | BBRG.Daily!C179 | 0.0108908237 | 0.000106971912 |
| 2025-03-20 | 562.20400 | 560.57830 | BBRG.Daily!C179 | BBRG.Daily!C178 | -0.0028916550 | 0.000011831921 |
| 2025-03-21 | 560.57830 | 560.76260 | BBRG.Daily!C178 | BBRG.Daily!C177 | 0.0003287676 | 0.000000048107 |
| 2025-03-24 | 560.76260 | 570.80490 | BBRG.Daily!C177 | BBRG.Daily!C176 | 0.0179082913 | 0.000301376208 |
| 2025-03-25 | 570.80490 | 572.17710 | BBRG.Daily!C176 | BBRG.Daily!C175 | 0.0024039738 | 0.000003444264 |
| 2025-03-26 | 572.17710 | 565.34630 | BBRG.Daily!C175 | BBRG.Daily!C174 | -0.0119382618 | 0.000155909255 |
| 2025-03-27 | 565.34630 | 563.84490 | BBRG.Daily!C174 | BBRG.Daily!C173 | -0.0026557174 | 0.000010264452 |
| 2025-03-28 | 563.84490 | 552.49010 | BBRG.Daily!C173 | BBRG.Daily!C172 | -0.0201381621 | 0.000427921481 |
| 2025-03-31 | 552.49010 | 556.19880 | BBRG.Daily!C172 | BBRG.Daily!C171 | 0.0067126995 | 0.000038002274 |
| 2025-04-01 | 556.19880 | 557.76980 | BBRG.Daily!C171 | BBRG.Daily!C170 | 0.0028245296 | 0.000005182127 |

Mean = **0.000548100998**. Sum of squared deviations = **0.001838171366**.

Daily SPY volatility = SQRT(sum of squared deviations / 13) = **0.011891080580**, or 1.18911%.

Leverage = MIN(4, 0.02 / volatility) = **1.681932929985**.

Shares = FLOOR(100000 × leverage / 555.38370) = FLOOR(302.84160842) = **302**. Do not round volatility or leverage before flooring shares.

### VWAP arithmetic for April 2's first entry

VWAP proxy = SUM(interval ending price × interval volume) / SUM(interval volume). These are observed interval volumes, not cumulative counters. No 16:00 residual is allocated backward.

| Source label | Available | Price source | Volume source | Price | Volume | Price × volume |
| --- | --- | --- | --- | --- | --- | --- |
| 09:30 | 10:00 | AV.Clean!B2349 | AV.Clean!C2349 | 555.38370 | 4,255,808 | 2,363,606,393.52960 |
| 10:00 | 10:30 | AV.Clean!B2348 | AV.Clean!C2348 | 557.64070 | 2,212,118 | 1,233,567,030.00260 |
| 10:30 | 11:00 | AV.Clean!B2347 | AV.Clean!C2347 | 558.83390 | 1,872,016 | 1,046,146,002.14240 |
| 11:00 | 11:30 | AV.Clean!B2346 | AV.Clean!C2346 | 560.08670 | 2,113,683 | 1,183,845,736.31610 |

Numerator = **5,827,165,161.99070**; denominator = **10,453,625**; proxy VWAP = **557.43009**. The workbook/CSV exposes each subsequent cumulative sum and each other requested day's inputs.

### All requested Model C trades

Commission and slippage below each include both legs. Direction +1 is long; −1 is short.

| Date | Direction | Entry | Exit | Shares | Entry price | Exit price | Gross P&L | Commission | Slippage | Net P&L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-04-02 | 1 | 11:30 | 12:00 | 302 | 560.08670 | 559.13220 | -288.25900 | 2.11400 | 0.60400 | -290.97700 |
| 2025-04-02 | 1 | 12:30 | 14:30 | 302 | 561.10090 | 557.79980 | -996.93220 | 2.11400 | 0.60400 | -999.65020 |
| 2025-07-03 | 1 | 11:00 | 13:00 | 501 | 623.57110 | 623.61100 | 19.98990 | 3.50700 | 1.00200 | 15.48090 |
| 2025-10-10 | -1 | 11:00 | 16:00 | 604 | 668.72500 | 653.02000 | 9,485.82000 | 4.22800 | 1.20800 | 9,480.38400 |
| 2025-11-21 | 1 | 12:00 | 13:30 | 378 | 660.82000 | 658.13000 | -1,016.82000 | 2.64600 | 0.75600 | -1,020.22200 |
| 2025-11-21 | 1 | 14:00 | 16:00 | 378 | 662.29000 | 659.03000 | -1,232.28000 | 2.64600 | 0.75600 | -1,235.68200 |

Signal values at each execution, recalculated from the underlying historical and volume rows:

| Date | Action | Time | Price | Upper | Lower | VWAP proxy |
| --- | --- | --- | --- | --- | --- | --- |
| 2025-04-02 | Entry | 11:30 | 560.08670 | 559.54864 | 553.61247 | 557.43009 |
| 2025-04-02 | Exit | 12:00 | 559.13220 | 560.00379 | 553.15927 | 557.72999 |
| 2025-04-02 | Entry | 12:30 | 561.10090 | 559.92788 | 553.23485 | 558.10635 |
| 2025-04-02 | Exit | 14:30 | 557.79980 | 560.21434 | 552.94962 | 559.31226 |
| 2025-07-03 | Entry | 11:00 | 623.57110 | 623.55999 | 617.69476 | 622.96997 |
| 2025-07-03 | Exit | 13:00 | 623.61100 | 624.04862 | 617.20909 | 623.44028 |
| 2025-10-10 | Entry | 11:00 | 668.72500 | 674.43126 | 669.90251 | 671.40110 |
| 2025-10-10 | Exit | 16:00 | 653.02000 | 675.28244 | 669.05387 | 660.93213 |
| 2025-11-21 | Entry | 12:00 | 660.82000 | 658.19349 | 649.17832 | 655.24029 |
| 2025-11-21 | Exit | 13:30 | 658.13000 | 658.68014 | 648.69338 | 656.44708 |
| 2025-11-21 | Entry | 14:00 | 662.29000 | 658.94747 | 648.42699 | 657.04522 |
| 2025-11-21 | Exit | 16:00 | 659.03000 | 659.20088 | 648.17447 | 658.13041 |

For each trade: gross P&L = direction × shares × (exit − entry); commission = 2 × shares × 0.0035; slippage = 2 × shares × 0.001; net = gross − commission − slippage. The Decisions sheet also computes the independent identity gross daily P&L = SUM(position before decision × shares × current-minus-previous price).

Day-level sizing and reconciliation:

| Date | Start equity | Leverage | Shares | Gross P&L | Total costs | Net P&L | Daily return |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-04-02 | 100,000.00000 | 1.68193 | 302 | -1,285.19120 | 5.43600 | -1,290.62720 | -1.29063% |
| 2025-07-03 | 103,627.93780 | 3.00980 | 501 | 19.98990 | 4.50900 | 15.48090 | 0.01494% |
| 2025-10-10 | 101,698.91600 | 4.00000 | 604 | 9,485.82000 | 5.43600 | 9,480.38400 | 9.32201% |
| 2025-11-21 | 112,150.37900 | 2.20968 | 378 | -2,249.10000 | 6.80400 | -2,255.90400 | -2.01150% |

On July 3, the 12:30-labeled interval is available at 13:00, and the separate 13:00 closing print is the liquidation reference. There is no afternoon trading. October 10 has **one short trade**, whose $9,480.38400 net gain divided by $101,698.91600 day-start equity gives +9.32201%. November 21 has **two long trades**: −$1,020.22200 and −$1,235.68200, totaling −$2,255.90400; divided by $112,150.37900, this gives −2.01150%.

## Sensitivity definitions fixed before running

Each case is run separately for A, B and C, with the same 168 scored sessions (April 2–December 1), initial capital, lookback, open proxy, gap adjustment, sizing rules and accounting conventions. No combined scenarios or return-driven parameter selection are used.

1. **Midpoint VWAP:** interval weight price is (previous endpoint + current endpoint)/2; the first interval uses its sole available endpoint. Volume and timestamp treatment stay unchanged. This is still a proxy, not exact VWAP.
2. **One 30-minute delay:** form a desired-position order on one grid observation and execute at the next available half-hour price without retrospectively rechecking that order. After execution, compute the next order using current information. Scheduled closing liquidation remains immediate and cancels pending orders, so no entry occurs at the close. This is a coarse execution stress, not an estimate of actual latency.
3. **VWAP entry gate:** additionally require price > VWAP for longs and price < VWAP for shorts, using the endpoint proxy. A is unaffected by this B/C-only variant. Baseline stop ordering remains unchanged.
4. **Exclude incomplete historical slots:** require all 14 previous sessions to have an observation at that clock time. Otherwise omit the entire discretionary decision, including entries and stop/reversal decisions, and retain the existing position. Forced close remains active. Do not drop whole sessions, stretch the window, carry the early close forward, or replace the divisor by 14 with an implicit zero. This interpretation of 'exclude slots' suppresses 75 decisions: 13:30–15:30 on the 14 sessions July 7–24 and on December 1. It can delay an existing position's exit; that effect is intentionally visible.
5. **Moderately higher costs:** commission $0.005 and slippage $0.002 per one-way share, versus $0.0035+$0.001. Total unit cost increases from $0.0045 to $0.007 (55.55556%). These preset stress amounts are not empirically estimated or optimized. Later daily share counts adjust mechanically to the changed equity path.

Statistics retain the baseline definitions: sample daily standard deviation × sqrt(252); Sharpe = mean / sample standard deviation × sqrt(252), zero risk-free rate; maximum drawdown includes initial capital. Trades are completed round trips and costs include both legs.

**Trade-change definition:** a baseline episode is unchanged only if direction, entry timestamp/price and exit timestamp/price all match a variant episode. A removed episode counts as changed. This avoids unreliable ordinal matching after an inserted/deleted trade. Share quantities and costs are excluded from that episode identity; quantity-only changes are reported separately. New/changed variant counts are also provided in the workbook and comparison CSV. This is not a claim that every unmatched trade has a uniquely identifiable replacement.

### Model A

| Case | Cumulative return | Ann. volatility | Sharpe | Max drawdown | Trades | Costs ($) | Baseline trades changed | Quantity-only changes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline replay | 3.59421% | 6.64939% | 0.82963 | -5.05948% | 95 | 138.33000 | 0 | 0 |
| Midpoint VWAP | 3.59421% | 6.64939% | 0.82963 | -5.05948% | 95 | 138.33000 | 0 | 0 |
| 30-minute delay | -3.17503% | 8.24890% | -0.54498 | -8.62534% | 89 | 123.61500 | 95 | 0 |
| VWAP entry gate | 3.59421% | 6.64939% | 0.82963 | -5.05948% | 95 | 138.33000 | 0 | 0 |
| Exclude incomplete slots | 3.61859% | 6.64941% | 0.83493 | -5.05948% | 94 | 136.92600 | 1 | 4 |
| Higher costs | 3.51556% | 6.65185% | 0.81221 | -5.08290% | 95 | 215.06800 | 0 | 8 |

### Model B

| Case | Cumulative return | Ann. volatility | Sharpe | Max drawdown | Trades | Costs ($) | Baseline trades changed | Quantity-only changes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline replay | 4.47404% | 7.24061% | 0.94237 | -2.83612% | 135 | 201.42000 | 0 | 0 |
| Midpoint VWAP | 4.47404% | 7.24061% | 0.94237 | -2.83612% | 135 | 201.42000 | 0 | 0 |
| 30-minute delay | 1.21342% | 6.61195% | 0.30628 | -3.97444% | 121 | 176.31000 | 135 | 0 |
| VWAP entry gate | 4.47404% | 7.24061% | 0.94237 | -2.83612% | 135 | 201.42000 | 0 | 0 |
| Exclude incomplete slots | 4.74571% | 7.24609% | 0.99549 | -2.83612% | 132 | 197.20800 | 4 | 25 |
| Higher costs | 4.36805% | 7.24134% | 0.92126 | -2.85028% | 135 | 313.04000 | 0 | 20 |

### Model C

| Case | Cumulative return | Ann. volatility | Sharpe | Max drawdown | Trades | Costs ($) | Baseline trades changed | Quantity-only changes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline replay | 11.13927% | 15.49954% | 1.09689 | -4.81698% | 135 | 534.91500 | 0 | 0 |
| Midpoint VWAP | 11.13927% | 15.49954% | 1.09689 | -4.81698% | 135 | 534.91500 | 0 | 0 |
| 30-minute delay | 3.90194% | 11.74713% | 0.54639 | -5.49987% | 121 | 459.23400 | 135 | 0 |
| VWAP entry gate | 11.13927% | 15.49954% | 1.09689 | -4.81698% | 135 | 534.91500 | 0 | 0 |
| Exclude incomplete slots | 12.21890% | 15.50578% | 1.19009 | -4.81472% | 132 | 520.77600 | 4 | 82 |
| Higher costs | 10.80734% | 15.49440% | 1.06823 | -4.86682% | 135 | 830.87200 | 0 | 75 |

### Interpretation without choosing a specification

- **Execution matters substantially:** the delayed case changes all baseline episodes. C's return falls to 3.90194% and its Sharpe to 0.54639; A becomes negative. This does not measure the cost of milliseconds of delay, but it shows dependence on which 30-minute observation is executable.
- **No observed VWAP-proxy trade sensitivity:** endpoint and midpoint proxies differ numerically on 2,172 retained observations, with a maximum absolute gap of $4.91721, but yield identical baseline trade episodes for all models. This verifies the variant was actually calculated. Equality of trades here does not prove true tick VWAP would be equivalent.
- **No baseline entry violates the extra VWAP condition**, so the entry gate changes no trades in B/C. This sample cannot distinguish those interpretations economically.
- **Historical half-day treatment affects a few episodes:** four of C's 135 baseline trades change. Three entries disappear (July 10, July 16, July 17), while the July 15 short retains its 13:00 entry but exits at 16:00 instead of 13:30. C ends with 132 round trips; 82 otherwise identical episodes have changed share counts through the equity path. This is an implementation-choice effect, not a reason to select the higher-return specification.
- **Higher costs reduce C's cumulative return to 10.80734%**, with costs rising to $830.87200. Timing and prices stay unchanged, although 75 otherwise identical episodes have changed share counts. This narrow cost stress does not validate baseline slippage, liquidity, financing, borrow, or market-impact assumptions.

## Model C concentration

Rank by the **net daily return**, not dollar P&L, with chronological date as a tie breaker. 'Dollar contribution' is the sum of the selected days' actual net dollar P&L, divided by the baseline total net profit ($11,139.26700). It is additive on the realized equity path and can exceed 100% because other days lose money.

'Return without days' sets the selected daily net returns to zero and compounds all 168 sessions: R_without = PRODUCT(1+r for remaining days)−1. It is not merely baseline return minus the selected daily returns or dollar P&L. The return difference is R_baseline−R_without. No strategy is rerun, no lookbacks are altered, and no later integer share counts are recomputed; this is ex-post concentration arithmetic, not a feasible rule for skipping future winners or losers.

| Selected tail | Count | Actual dollar contribution | Share of total net profit | Compounded return of selected days | Cumulative return without | Return difference (pp) |
| --- | --- | --- | --- | --- | --- | --- |
| best | 1 | 9,480.38400 | 85.10779% | 9.32201% | 1.66230% | 9.47697 |
| best | 3 | 15,760.74320 | 141.48815% | 15.99450% | -4.18574% | 15.32501 |
| best | 5 | 19,903.23510 | 178.67634% | 20.74002% | -7.95159% | 19.09086 |
| worst | 1 | -2,255.90400 | -20.25182% | -2.01150% | 13.42072% | -2.28146 |
| worst | 3 | -5,829.46980 | -52.33262% | -5.35270% | 17.42466% | -6.28539 |
| worst | 5 | -8,720.94200 | -78.29009% | -8.02300% | 20.83376% | -9.69450 |

Individual selected days:

| Tail | Rank | Date | Daily return | Net P&L ($) |
| --- | --- | --- | --- | --- |
| best | 1 | 2025-10-10 | 9.32201% | 9,480.38400 |
| best | 2 | 2025-04-09 | 3.49744% | 3,525.75720 |
| best | 3 | 2025-11-20 | 2.51801% | 2,754.60200 |
| best | 4 | 2025-04-04 | 2.49785% | 2,471.84890 |
| best | 5 | 2025-11-13 | 1.55448% | 1,670.64300 |
| worst | 1 | 2025-11-21 | -2.01150% | -2,255.90400 |
| worst | 2 | 2025-09-17 | -1.78136% | -1,866.91960 |
| worst | 3 | 2025-09-18 | -1.65797% | -1,706.64620 |
| worst | 4 | 2025-10-03 | -1.55071% | -1,600.84500 |
| worst | 5 | 2025-04-02 | -1.29063% | -1,290.62720 |

The best day supplies 85.10779% of realized dollar net profit. Without the best day, cumulative return is 1.66230%; without the best three or five, it is −4.18574% or −7.95159%. The result is therefore materially concentrated in a small number of favorable sessions. Removing the worst one, three or five days raises return to 13.42072%, 17.42466% or 20.83376%, respectively. These paired tail views show both sides of the same hindsight exercise.

## Verification and preservation

- 34 independently recomputed baseline feature, P&L, sizing and exact-episode comparisons pass; no baseline functions are imported.
- Every source-cell reference in the manual tables is checked against the original XLSX using a separate read path.
- 2,774 workbook formula results are checked against independently computed values; input perturbation and restoration verifies recalculation. A formula-error scan finds none. Saved formula caches are checked after export, and all nine sheets are visually reviewed. Native Microsoft Excel recalculation has not been tested.
- All 18 case/model ledgers reconcile inventory P&L, completed trades, event costs and daily equity; delayed discretionary executions are one interval after their signal; half-day liquidation and zero overnight inventory are checked.
- SHA-256 checks confirm that all 30 protected files (original workbook, baseline code/test/package and baseline-output files) remain unchanged.
- No model is designated 'best'; no baseline assumption is adopted or revised. Original uncertainty about actual opens, true VWAP, timestamp semantics and executable fills remains.

## Files and reproduction

- `validation_tables.xlsx`: primary manual workbook with live arithmetic.
- `manual_noise_history.csv`, `april02_1130_noise_14.csv`: historical raw values and source references.
- `manual_volatility_returns.csv`, `april02_volatility_14.csv`, `manual_sizing.csv`: all lagged returns, variance terms and sizing.
- `manual_decisions.csv`, `manual_events.csv`, `manual_trades.csv`: full chronological details for the four days.
- `sensitivity_summary.csv`, `trade_comparison.csv`, `excluded_decision_slots.csv`: sensitivity metrics and episode-level differences.
- `C_concentration.csv`, `C_ranked_days.csv`: both contribution definitions and exact tail selections.
- `scenarios/<case>/<model>_daily.csv`, `_trades.csv`, `_decisions.csv`, `_events.csv`: all independent replay results, including a matched baseline replay.
- `independent_reconciliation.csv`, `final_verification.json`, `validation_manifest.json`, `baseline_hashes_before.json`: reproducibility evidence.

From the original workspace, use the bundled Python executable to run `validation/independent_validation.py`, then bundled Node for `validation/build_workbook.mjs`, then Python for `validation/verify_outputs.py` and `validation/write_report.py`. The original workbook location is read from the untouched baseline manifest. Portable use requires pandas, numpy, openpyxl and the Artifact Tool package; the delivered workbook and CSVs can be reviewed without those packages.

This completes the requested validation/sensitivity phase while preserving the baseline. Vendor metadata, an actual market-open series, or later authorized author-code comparison would address uncertainties this arithmetic exercise cannot settle.
