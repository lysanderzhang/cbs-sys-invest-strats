from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/validation'
p=json.loads((O/'workbook_data.json').read_text())
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(str(x) for x in row)+' |' for row in rows])+'\n'
def pct(x):return f'{100*x:.5f}%'
def n(x):return f'{x:,.5f}'
text=['''# Independent reconstruction, ambiguity sensitivity, and concentration

The original baseline files and assumptions remain unchanged. This phase reconstructs source observations directly in a separate program without importing or calling `strategy.py`. It uses explicit sums for historical estimates and inventory-times-price-change accounting for equity, rather than the original rolling calculations and realized-trade equity ledger. Only after this replay are frozen baseline CSVs opened for reconciliation.

All 34 reconciliation checks pass. All A/B/C trade episodes match, and the largest numerical difference among checked fields is less than $0.000000001. This is implementation-level corroboration by a second code path, **not blind third-party validation**: the same AI generated it with knowledge of the baseline conventions. It does not validate Bloomberg timestamp semantics, actual opens, true VWAP, or executable fill prices. No author code was consulted.

## Manual reproduction tables

`validation_tables.xlsx` contains formulas, raw source values, exact source sheet/cell addresses, and chronological position/P&L calculations. Read Summary, then Noise/Volatility/VWAP, Decisions and Trades. Daily Equity provides the independently reconstructed beginning capital for every scored session. The separate CSVs expose the same inputs without formatting.

The four requested days have 46 decision rows and six round trips. Supporting tables include 644 historical Noise observations and 56 lagged daily-return observations: all clock-time histories needed for all four days, not just April 2 at 11:30. Availability timestamps are baseline-inferred bar endpoints; all original proxy assumptions are retained.

The workbook is a manual arithmetic model, not a full interactive backtester. Its formulas recalculate raw-price ratios, variance, sizing, VWAP, selected-day state transitions, trade P&L and concentration. Daily Equity's independently replayed gross/cost inputs and sensitivity results are fixed snapshots. Editing a source value locally does not resimulate all future historical trades or re-rank concentration dates. The Python replay is supplied for that purpose.

### April 2: all 14 observations for the 11:30 Noise Area

For each historical session, O is AV.Clean's 09:30-labeled price (the baseline 10:00 open proxy), and P is its 11:00-labeled price (available at 11:30). Calculate m=ABS(P/O-1). Source columns below are literal cells in the original workbook.
''']
noise=[x for x in p['noise'] if x['target_date']=='2025-04-02' and x['slot']=='11:30']
text.append(table(['Historical day','Open proxy','11:30 price','Open cell','Price cell','Absolute move'],
 [[x['historical_date'],n(x['open_proxy']),n(x['historical_price']),x['open_cell'],x['price_cell'],f"{x['absolute_move']:.10f}"] for x in noise]))
sigma=sum(x['absolute_move'] for x in noise)/14
first=p['sizing'][0];apr=[x for x in p['decisions'] if x['date']=='2025-04-02' and x['slot']=='11:30'][0]
text.append(f'''Sum of the 14 absolute moves = {sum(x['absolute_move'] for x in noise):.12f}. Divide by 14 to get **{sigma:.12f}**, or {pct(sigma)}.

- Current proxy open: {n(first['open_proxy'])} from {first['open_source_cell']}.
- Previous daily close: {n(first['previous_close'])} from {first['previous_close_cell']}.
- Upper = MAX({n(first['open_proxy'])}, {n(first['previous_close'])}) × (1 + {sigma:.12f}) = **{n(apr['upper'])}**.
- Lower = MIN({n(first['open_proxy'])}, {n(first['previous_close'])}) × (1 − {sigma:.12f}) = **{n(apr['lower'])}**.
- At 11:30, price {n(apr['price'])} exceeds upper {n(apr['upper'])}, so a flat Model C enters long.

### April 2: all 14 lagged daily returns

Each simple return is closing price / previous closing price − 1. The source rows run from the March 12 prerequisite close through the April 1 close; the first return is March 13, and April 2's return is excluded. Squared deviations below use the full-precision mean, not a rounded displayed mean.
''')
vol=[x for x in p['volatility'] if x['target_date']=='2025-04-02']
text.append(table(['Return date','Previous close','Close','Prior source','Close source','Return','Squared deviation'],
 [[x['return_date'],n(x['previous_close']),n(x['close']),x['previous_close_cell'],x['close_cell'],f"{x['spy_return']:.10f}",f"{x['squared_deviation']:.12f}"] for x in vol]))
text.append(f'''Mean = **{first['mean_return']:.12f}**. Sum of squared deviations = **{first['squared_deviation_sum']:.12f}**.

Daily SPY volatility = SQRT(sum of squared deviations / 13) = **{first['prior_vol']:.12f}**, or {pct(first['prior_vol'])}.

Leverage = MIN(4, 0.02 / volatility) = **{first['sizing_leverage']:.12f}**.

Shares = FLOOR(100000 × leverage / 555.38370) = FLOOR({100000*first['sizing_leverage']/first['open_proxy']:.8f}) = **302**. Do not round volatility or leverage before flooring shares.

### VWAP arithmetic for April 2's first entry

VWAP proxy = SUM(interval ending price × interval volume) / SUM(interval volume). These are observed interval volumes, not cumulative counters. No 16:00 residual is allocated backward.
''')
april_early=[x for x in p['decisions'] if x['date']=='2025-04-02' and x['slot']<='11:30']
text.append(table(['Source label','Available','Price source','Volume source','Price','Volume','Price × volume'],
 [[x['source_timestamp'][11:16],x['slot'],x['interval_price_cell'],x['volume_cell'],n(x['interval_price']),f"{x['volume']:,}",n(x['interval_price_times_volume'])] for x in april_early]))
text.append(f"Numerator = **{n(apr['cumulative_price_volume'])}**; denominator = **{apr['cumulative_volume']:,.0f}**; proxy VWAP = **{n(apr['vwap_endpoint'])}**. The workbook/CSV exposes each subsequent cumulative sum and each other requested day's inputs.\n")
text.append('### All requested Model C trades\n\nCommission and slippage below each include both legs. Direction +1 is long; −1 is short.\n')
text.append(table(['Date','Direction','Entry','Exit','Shares','Entry price','Exit price','Gross P&L','Commission','Slippage','Net P&L'],
 [[x['date'],x['direction'],x['entry_timestamp'][11:16],x['exit_timestamp'][11:16],x['shares'],n(x['entry_price']),n(x['exit_price']),n(x['gross_pnl']),n(x['commission']),n(x['slippage']),n(x['net_pnl'])] for x in p['trades']]))
text.append('Signal values at each execution, recalculated from the underlying historical and volume rows:\n')
signal_rows=[]
for t in p['trades']:
    for action,prefix in [('Entry','entry'),('Exit','exit')]:
        signal_rows.append([t['date'],action,t[prefix+'_timestamp'][11:16],n(t[prefix+'_price']),n(t[prefix+'_upper']),n(t[prefix+'_lower']),n(t[prefix+'_vwap'])])
text.append(table(['Date','Action','Time','Price','Upper','Lower','VWAP proxy'],signal_rows))
text.append('''For each trade: gross P&L = direction × shares × (exit − entry); commission = 2 × shares × 0.0035; slippage = 2 × shares × 0.001; net = gross − commission − slippage. The Decisions sheet also computes the independent identity gross daily P&L = SUM(position before decision × shares × current-minus-previous price).

Day-level sizing and reconciliation:
''')
selected_days=[x for x in p['daily'] if x['date'] in [z['date'] for z in p['sizing']]]
text.append(table(['Date','Start equity','Leverage','Shares','Gross P&L','Total costs','Net P&L','Daily return'],
 [[x['date'],n(x['start_equity']),n(x['sizing_leverage']),x['shares'],n(x['gross_pnl']),n(x['costs']),n(x['net_pnl']),pct(x['daily_return'])] for x in selected_days]))
text.append('''On July 3, the 12:30-labeled interval is available at 13:00, and the separate 13:00 closing print is the liquidation reference. There is no afternoon trading. October 10 has **one short trade**, whose $9,480.38400 net gain divided by $101,698.91600 day-start equity gives +9.32201%. November 21 has **two long trades**: −$1,020.22200 and −$1,235.68200, totaling −$2,255.90400; divided by $112,150.37900, this gives −2.01150%.

## Sensitivity definitions fixed before running

Each case is run separately for A, B and C, with the same 168 scored sessions (April 2–December 1), initial capital, lookback, open proxy, gap adjustment, sizing rules and accounting conventions. No combined scenarios or return-driven parameter selection are used.

1. **Midpoint VWAP:** interval weight price is (previous endpoint + current endpoint)/2; the first interval uses its sole available endpoint. Volume and timestamp treatment stay unchanged. This is still a proxy, not exact VWAP.
2. **One 30-minute delay:** form a desired-position order on one grid observation and execute at the next available half-hour price without retrospectively rechecking that order. After execution, compute the next order using current information. Scheduled closing liquidation remains immediate and cancels pending orders, so no entry occurs at the close. This is a coarse execution stress, not an estimate of actual latency.
3. **VWAP entry gate:** additionally require price > VWAP for longs and price < VWAP for shorts, using the endpoint proxy. A is unaffected by this B/C-only variant. Baseline stop ordering remains unchanged.
4. **Exclude incomplete historical slots:** require all 14 previous sessions to have an observation at that clock time. Otherwise omit the entire discretionary decision, including entries and stop/reversal decisions, and retain the existing position. Forced close remains active. Do not drop whole sessions, stretch the window, carry the early close forward, or replace the divisor by 14 with an implicit zero. This interpretation of 'exclude slots' suppresses 75 decisions: 13:30–15:30 on the 14 sessions July 7–24 and on December 1. It can delay an existing position's exit; that effect is intentionally visible.
5. **Moderately higher costs:** commission $0.005 and slippage $0.002 per one-way share, versus $0.0035+$0.001. Total unit cost increases from $0.0045 to $0.007 (55.55556%). These preset stress amounts are not empirically estimated or optimized. Later daily share counts adjust mechanically to the changed equity path.

Statistics retain the baseline definitions: sample daily standard deviation × sqrt(252); Sharpe = mean / sample standard deviation × sqrt(252), zero risk-free rate; maximum drawdown includes initial capital. Trades are completed round trips and costs include both legs.

**Trade-change definition:** a baseline episode is unchanged only if direction, entry timestamp/price and exit timestamp/price all match a variant episode. A removed episode counts as changed. This avoids unreliable ordinal matching after an inserted/deleted trade. Share quantities and costs are excluded from that episode identity; quantity-only changes are reported separately. New/changed variant counts are also provided in the workbook and comparison CSV. This is not a claim that every unmatched trade has a uniquely identifiable replacement.
''')
labels={'baseline_replay':'Baseline replay','midpoint_vwap':'Midpoint VWAP','delay_30m':'30-minute delay','vwap_entry_gate':'VWAP entry gate','exclude_incomplete_slots':'Exclude incomplete slots','higher_costs':'Higher costs'}
for model in 'ABC':
    text.append('### Model '+model+'\n')
    rows=[x for x in p['sensitivity'] if x['model']==model]
    text.append(table(['Case','Cumulative return','Ann. volatility','Sharpe','Max drawdown','Trades','Costs ($)','Baseline trades changed','Quantity-only changes'],
      [[labels[x['case']],pct(x['cumulative_return']),pct(x['annualized_volatility']),n(x['sharpe']),pct(x['maximum_drawdown']),x['trades'],n(x['total_costs']),x['baseline_trades_changed'],x['shares_changed_same_episode']] for x in rows]))
text.append('''### Interpretation without choosing a specification

- **Execution matters substantially:** the delayed case changes all baseline episodes. C's return falls to 3.90194% and its Sharpe to 0.54639; A becomes negative. This does not measure the cost of milliseconds of delay, but it shows dependence on which 30-minute observation is executable.
- **No observed VWAP-proxy trade sensitivity:** endpoint and midpoint proxies differ numerically on 2,172 retained observations, with a maximum absolute gap of $4.91721, but yield identical baseline trade episodes for all models. This verifies the variant was actually calculated. Equality of trades here does not prove true tick VWAP would be equivalent.
- **No baseline entry violates the extra VWAP condition**, so the entry gate changes no trades in B/C. This sample cannot distinguish those interpretations economically.
- **Historical half-day treatment affects a few episodes:** four of C's 135 baseline trades change. Three entries disappear (July 10, July 16, July 17), while the July 15 short retains its 13:00 entry but exits at 16:00 instead of 13:30. C ends with 132 round trips; 82 otherwise identical episodes have changed share counts through the equity path. This is an implementation-choice effect, not a reason to select the higher-return specification.
- **Higher costs reduce C's cumulative return to 10.80734%**, with costs rising to $830.87200. Timing and prices stay unchanged, although 75 otherwise identical episodes have changed share counts. This narrow cost stress does not validate baseline slippage, liquidity, financing, borrow, or market-impact assumptions.

## Model C concentration

Rank by the **net daily return**, not dollar P&L, with chronological date as a tie breaker. 'Dollar contribution' is the sum of the selected days' actual net dollar P&L, divided by the baseline total net profit ($11,139.26700). It is additive on the realized equity path and can exceed 100% because other days lose money.

'Return without days' sets the selected daily net returns to zero and compounds all 168 sessions: R_without = PRODUCT(1+r for remaining days)−1. It is not merely baseline return minus the selected daily returns or dollar P&L. The return difference is R_baseline−R_without. No strategy is rerun, no lookbacks are altered, and no later integer share counts are recomputed; this is ex-post concentration arithmetic, not a feasible rule for skipping future winners or losers.
''')
text.append(table(['Selected tail','Count','Actual dollar contribution','Share of total net profit','Compounded return of selected days','Cumulative return without','Return difference (pp)'],
 [[x['tail'],x['k'],n(x['selected_net_pnl']),pct(x['selected_dollar_pnl_share']),pct(x['selected_compound_return']),pct(x['cumulative_return_without']),n(100*x['return_difference'])] for x in p['concentration']]))
text.append('Individual selected days:\n')
text.append(table(['Tail','Rank','Date','Daily return','Net P&L ($)'],[[x['tail'],x['rank'],x['date'],pct(x['daily_return']),n(x['net_pnl'])] for x in p['ranked_days']]))
text.append('''The best day supplies 85.10779% of realized dollar net profit. Without the best day, cumulative return is 1.66230%; without the best three or five, it is −4.18574% or −7.95159%. The result is therefore materially concentrated in a small number of favorable sessions. Removing the worst one, three or five days raises return to 13.42072%, 17.42466% or 20.83376%, respectively. These paired tail views show both sides of the same hindsight exercise.

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
''')
(O/'VALIDATION_REPORT.md').write_text('\n'.join(text))
print('Wrote VALIDATION_REPORT.md')
