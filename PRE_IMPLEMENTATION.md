# Pre-implementation review

Completed before strategy code was written. Sources are the three supplied files only. No author code, linked implementations, indicators, or prior-paper implementations were consulted. Document instructions are assignment requirements to describe, not authority to expand this user-requested first implementation.

## Assignment requirements (hw1.pdf, pages 1–4)

- Use an AI tool to generate a replication; document tool choice and why, prompts, iterations, errors, corrections, accuracy checks, and selected/omitted paper variants with reasons.
- Test on real data, identify suspected anomalies, report return/comparison statistics and discuss robustness and the interaction between available data and chosen methods.
- Independently verify the final AI implementation, potentially by manual calculations, separate code, another AI, or later author-code comparison. Author code is excluded from this implementation stage by the user.
- Ultimately assess the strategy, its variants, investor suitability, practical implementation, conditions driving profitability, risks, and possible improvements; critically review the paper and its presentation.
- Submit an understandable write-up with an initial answer summary, explanations of main formulas and reproducible steps, and at least five decimal places where appropriate. Spreadsheet printouts require row/column headings. Groups may have at most three members and submit once. Stated deadline: September 22, 2026, 5 pm EST; the document's EST wording is not silently converted to EDT.
- This delivery covers the requested first implementation of A/B/C, diagnostics, and a verification plan. It does not claim to complete the student's independent verification or final critique. VIX, dealer gamma/RSI, daily OHLC pattern studies, other instruments, and parameter optimization are out of scope.

## Paper specification

Paper version September 22, 2025, with main historical sample May 2007–April 2024; later FAQ results use different endpoints. Page numbers below are PDF page numbers, matching printed numbering.

For session d, time h, true market open O, previous session close C, and price P:

1. m[d,h] = abs(P[d,h]/O[d] - 1).
2. sigma_noise[d,h] = mean(m[d-i,h], i=1,...,14). This is a mean absolute move, NOT a standard deviation (pp. 6–7).
3. U[d,h] = max(O[d], C[d-1]) * (1 + sigma_noise[d,h]); L[d,h] = min(O[d], C[d-1]) * (1 - sigma_noise[d,h]). Multiplier is 1.
4. Evaluate only HH:00/HH:30, first entry 10:00 in the paper (pp. 9, 21). Above U enter long; below L enter short. A holds through the Noise Area and reverses at the opposite boundary. Flatten at scheduled session close (p. 9).
5. B exits a long when P < max(U,VWAP), and a short when P > min(L,VWAP), only on the decision grid. Stops are current dynamic levels, not running extrema (p. 13). VWAP uses market-hours data only.
6. A/B shares = floor(previous equity / O). Initial equity $100,000 (p. 10).
7. C uses the sample standard deviation (denominator 13) of the previous 14 daily SPY returns. Leverage = min(4,0.02/sigma_SPY); shares = floor(previous equity * leverage / O) (p. 15). Shares fixed for the day, including reentries.
8. Costs per one-way share: commission $0.0035, slippage $0.001 (pp. 10, 24–25). Slippage experiment references minute opening prices, which are absent here.

## Workbook audit before implementation

Workbook has three sheets, newest first:

| Sheet | Rows | Columns | Interpretation |
|---|---:|---|---|
| BBRG.Intraday | 2542 | blank column, Time Stamp, Last Price, Volume, SMAVG (15) | Raw half-hour records; moving average is unused |
| BBRG.Daily | 197 | same five headings | Daily close/volume, February 20–December 1, 2025; useful prior close/volatility history, no open/high/low |
| AV.Clean | 2544 | Time Stamp, Last Price, Volume, AV | Primary cleaned observations, March 13–December 1, 2025 |

AV.Clean has no missing cells, duplicate timestamps, negative volumes, or nonpositive prices. It contains 180 days with 14 rows, and two days with 12 rows. All daily-sheet sessions in the intraday span are represented. Timestamps lack timezone metadata; treat them as New York local session times. Normal labels run 09:30 through 16:00 at 30-minute intervals.

**Volume is not a day-to-time cumulative counter.** It decreases 1,181 times within sessions. The non-16:00 cleaned values match the raw interval volumes. Of 182 closing rows, 176 volumes differ from raw (including two added rows); 175 daily sums exactly reconcile to daily-sheet volume. Six unmodified small raw 16:00 observations leave deficits. March 13 overcounts daily volume by exactly its first-row volume.

Daily sum minus daily-sheet volume: March 13 +3,376,733; April 17 -39,823,340; April 23 -29,277,792; April 25 -23,664,489; May 9 -12,974,365; September 22 -20,887,306; November 3 -15,604,940. Other days reconcile. The large residuals at 16:00 cannot be assumed to be closing-auction volume or allocated to earlier intervals. The file contains values only, no formulas establishing their provenance.

Cleaned prices match overlapping raw prices. Final cleaned prices differ from daily closes by at most $0.00030, consistent with small rounding differences. The 15:30 and 16:00 prices are exactly equal on 121/182 days, and differ by at most $0.29830 across all days. This strongly suggests start-labeled half-hour bars followed by a separate closing print; it is evidence, not confirmed Bloomberg metadata.

On both July 3 and November 28 the 12:30 price equals the 13:00 price and all later prices. Labels 13:30 and 14:30 are missing, while 14:00, 15:00, 15:30 are stale zero-volume observations and 16:00 contains a large residual volume (18,991,361 and 17,387,935 respectively). These are not tradable afternoon observations.

## Explicit initial choices and unavoidable deviations

- Treat rows 09:30–15:30 as start-labeled interval endpoints, available label+30 minutes. On early-close days retain only labels 09:30–12:30. Retain 16:00 normal/13:00 early-close print only as liquidation price, not an extra interval. No future daily totals enter intraday VWAP.
- True 09:30 open is absent. Use the first interval endpoint, available at 10:00, as O_proxy. Do not trade at that anchor, so earliest possible entry is 10:30. Noise moves exclude the opening half hour and gap boundaries mix overnight and first-half-hour moves. This is a data-constrained approximation, not an exact replication.
- Treat supplied interval volume as incremental. Construct cumulative volume from those increments. A separately exposed cumulative-input function will difference only truly cumulative inputs and reject negative differences.
- Approximate VWAP by sum(interval ending price * interval volume)/sum(interval volume). This uses only information available at the decision time, but misses within-interval price/volume covariance and unallocated volume. Keep endpoint versus adjacent-endpoint midpoint weighting selectable; do not claim either is exact or test sensitivity yet.
- Use exactly the previous 14 session rows for Noise Area. For afternoon slots absent on a known early-close day, average the available 13 observations in that window, explicitly logging the count; never reach back to a 15th session or carry the early close forward. Full 14-session history is required before trading. This deviates from the paper's literal divisor 14, which does not address half days.
- Use supplied daily closes for previous-close gaps, simple close-to-close returns, and lagged volatility, with ddof=1. No dividend adjustment metadata is supplied. Do not manufacture dividends or splice outside data.
- Final first-delivery choice: B/C entries use Noise boundaries only, preserving the user's same-signal requirement. If an entry already violates VWAP, its stop is first evaluated at the next decision time. Exit/reverse priority first, no same-direction exit/reentry at the same timestamp; later reentry allowed without a new crossing event. An optional entry VWAP filter is exposed for later sensitivity. The initial pre-code choice was an entry filter; review corrected that before delivery (see CHANGELOG.md).
- Strict inequalities for entry and stop crossing; equality preserves existing exposure. Reversal closes and opens separately, charging both legs. End-of-day liquidation overrides all signals and prohibits new entries.
- Contemporaneous endpoint execution is an idealized zero-latency fill, with adverse slippage charged separately. Signals never earn the return that formed them. Missing subminute prices prevent exact executable fills. A separately configurable one-grid-step execution delay is provided for later investigation, not optimized.
- Daily share count uses beginning equity and proxy open; leverage capped at 4 in the sizing formula, not continuously at marked market value. Actual entry exposure can exceed target as price moves; log both.
- No financing, stock borrow, interest on cash/short proceeds, exchange fees, minimum commission, dividend cash flows, or price-impact model is invented. $0.001 slippage is retained as requested, not calibrated or verified from these data.

## Paper ambiguities to preserve for review

Entry versus exit ordering; whether VWAP filters entries; level tests versus actual crossings and reentry rules; strict versus inclusive thresholds; exact signal-to-fill timestamps; precise VWAP input price and auction handling; whether the term trailing implies a ratchet (equations use current levels); dividend/adjustment conventions and definition of daily return; half-day historical slots; missing-data rules; zero-volatility sizing; benchmark costs; Sharpe risk-free rate, annualization, and hit-ratio denominator. Main-text trade and daily hit ratios differ; report both separately. The paper's 2% target scales SPY exposure, not realized strategy volatility.
