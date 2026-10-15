# HW2 Momentum Strategy — Agent Execution Specification

**Course:** FINCB9339 / B9339, Systematic Investment Strategies, Fall 2026  
**Assignment:** Homework 2, investor pitch  
**Owner:** Hanyu Zhang  
**Specification date:** October 3, 2026  
**Data-access constraint:** No WRDS access. Yahoo Finance is approved; Databento is approved as an optional data source using existing authorized access.  
**Assignment deadline:** October 5, 2026, 5:00 p.m. Eastern, as stated in the handout. The handout labels this “EST”; confirm the intended timezone in the course submission portal because New York observes EDT on that date. Do not delay research for this clarification.

## 1. Your task and authority

Act as a quantitative researcher, backtest engineer, and academic presentation collaborator. Execute this specification: acquire data, implement two momentum prototypes, validate the accounting and timing, evaluate the evidence, and prepare a reproducible investor pitch. Do not stop after proposing a plan or delivering download instructions.

The research question is:

> Can a simple, predetermined momentum strategy improve its investment usefulness through risk management, without relying on hindsight, excessive parameter tuning, or unrealistic trading assumptions?

Implement these two separate projects:

1. **Prototype A: crash-aware US equity momentum factor.** Use Kenneth French momentum returns to examine volatility scaling and an observable market-stress overlay. This is an academic factor experiment, not a stock-level executable strategy.
2. **Prototype B: cross-asset ETF dual momentum.** Use real ETF total returns to examine relative selection, an absolute momentum filter, and conservative portfolio volatility scaling. This is the preferred executable investor-pitch candidate if data and evidence support it.

WRDS/CRSP acquisition and stock-level strategy construction are out of scope for this run. Do not ask the user to obtain WRDS access. Complete both minimum prototypes before considering additional strategy features. Prefer Prototype B for the main assets-under-management pitch because its holdings, turnover, and execution can be modeled directly. Use A to explain the course's equity momentum crash mechanism and investigate risk management. If B produces weak evidence, report that honestly; do not switch to A solely because its Sharpe ratio is higher. A may be the main research pitch if clearly labeled and accompanied by an implementation roadmap and limits on investability claims.

Proceed autonomously with reversible research and local development. Ask only for genuinely blocking access, missing course requirements, or material investor preferences. Continue the unblocked prototype while another data source is unavailable. Do not place trades, buy data, publish a repository, send messages, or submit the assignment. Never embed credentials in code or outputs.

## 2. Read these inputs first

Use the supplied files; do not rely on a previous assistant's summary as authoritative evidence. The paths below are the current workspace paths. If transferred to another workspace, locate the same filenames in the provided attachments and record the resolved paths.

| Input | Current path | Required use |
|---|---|---|
| Homework prompt | `upload/hw2.md` | Submission requirements and evaluation checklist |
| Lecture slides | `upload/2 momentum.md` | Instructor's terminology, notation, and strategy choices |
| Daniel & Moskowitz | `upload/Momentum crashes.md` | Panic states, rebound mechanism, conditional momentum risk |
| Asness et al. | `upload/Fact, Fiction and Momentum Investing.md` | Momentum evidence, implementation, trading costs, diversification |
| Kolanovic & Wei | `upload/Momentum Strategies Across Asset Classes Risk Factor Approach to Trend Following.md` | Cross-asset design choices, risk factors, overfitting concerns |
| Baltas & Kosowski | `upload/Momentum Strategies in Futures Markets and Trend-Following Funds.md` | Time-series momentum, volatility normalization, futures implementation |

The base directory at specification creation is `/workspace/scratch/60f6d02d3020`. Do not hardcode it into reusable Python modules.

Read relevant methodological sections in context; extraction may have scrambled equations or multi-column text. Flag ambiguous formulas rather than guessing. Use original publisher/author versions only when necessary to resolve ambiguity, and record that source.

Create `research/requirements_matrix.md` mapping every homework requirement to a report section, slide, and supporting artifact. The assignment requires:

- A clear objective: raising assets, working capital, or both.
- Strategy landscape and similarities/differences.
- Main idea and enough methodological and results detail to reproduce it.
- Innovation, **if any**, and competitive advantages supported by evidence.
- Robustness of evidence.
- Feasibility: costs, liquidity, capacity, target capital where relevant.
- Anticipated investor questions and answers.
- Explanations of formulas and software output; numbers alone are insufficient.
- A first-page summary, preferably; appropriate numeric outputs to at least five decimal places.

Default pitch objective: **raise assets for a transparent, monthly managed cross-asset ETF portfolio**. Use an illustrative USD 10 million initial mandate for capacity calculations, plus USD 1 million and USD 50 million scenarios. These are research assumptions, not actual commitments or validated fund capacity.

## 3. Important corrections to the initial brainstorming

1. A risk-adjusted **stock-ranking** signal and **portfolio volatility targeting** are different interventions. French aggregate momentum returns permit the latter; they do not permit new constituent rankings, sector neutrality, or individual-stock turnover calculations.
2. French Mom is not simply a top-decile-minus-bottom-decile stock portfolio. Its documented size/momentum construction differs. Cite the downloaded series' actual methodology; never relabel it as your reconstructed stock strategy.
3. A bear-market/VIX exposure rule is a heuristic motivated by the readings. It is not a replication of Daniel–Moskowitz's conditional mean/variance strategy. Volatility targeting alone also is not that replication.
4. Momentum crash mechanics vary by strategy. Short losers rebounding is particularly relevant to equity cross-sectional long–short momentum; a long-only ETF strategy has different risks. Do not assume all trend following has the same skewness or crash behavior.
5. Volatility targeting does not guarantee a higher Sharpe ratio, lower drawdown, or better skewness. Results tables must report measured effects, including failures.
6. An ETF universe chosen today still has retrospective universe-selection risk even if you respect inception dates. Do not describe it as completely free of survivorship bias.
7. Published research and lectures inform these rules. A historical holdout is a useful discipline, but is not pristine, genuinely unseen out-of-sample evidence.
8. Established overlays do not constitute a newly discovered anomaly. Position the contribution as transparent implementation, a controlled comparison, and an evidence-based product design.

## 4. Work order and scope control

Follow the stages below in order. Record completion, failed attempts, and deviations in `research/progress.md`.

| Stage | Action | Completion artifact |
|---|---|---|
| 1 | Read inputs; map requirements; inspect existing project | Requirements matrix and source map |
| 2 | Freeze hypotheses, defaults, dates, evaluation protocol | Research plan and config with timestamp/hash |
| 3 | Download/cache public factor and ETF data | Raw files, manifests, data-quality report |
| 4 | Implement accounting and timing; pass targeted tests | Test report and worked examples |
| 5 | Run A baseline and all specified overlays | Factor results and exposure audit |
| 6 | Run B baseline and specified additions | ETF results, holdings, turnover, costs |
| 7 | Run predetermined robustness and historical holdout | Robustness tables, paired uncertainty estimates |
| 8 | Select pitch emphasis using fixed criteria | Recommendation and limitations memo |
| 9 | Prepare report and presentation | Report, slides, references, formulas |
| 10 | Reproduce and inspect final outputs | Clean-run log and acceptance checklist |

Suggested effort budget, not a promise: stages 1–3 about 1.5–2 hours; 4–6 about 3–4 hours; 7–8 about 1–2 hours; 9–10 about 2–3 hours. Build a working minimum early. Limit retries for any blocked provider to two meaningful attempts, then implement an input adapter and document the blocker. Avoid unrelated infrastructure, ML forecasts, GARCH fitting, full futures roll engineering, and exhaustive optimization.

If a partial result is unavoidable, prioritize valid data, correct minimum backtests, and an honest pitch over extra variants. Never fabricate successful downloads or performance.

## 5. Research plan to freeze before inspecting strategy results

Write `research/research_plan.md` before performance analysis. Include these hypotheses:

- **A1:** Scaling factor exposure using trailing volatility may reduce realized risk relative to a static exposure.
- **A2:** Additional de-risking after market weakness and elevated implied volatility may improve downside outcomes; it may also miss profitable rebounds and reduce returns.
- **B1:** Relative ETF selection may outperform an equal-weight universe benchmark on some return/risk measures.
- **B2:** An absolute momentum filter may reduce exposure during prolonged declines, with possible whipsaw and opportunity costs.
- **B3:** A conservative volatility cap may stabilize risk but lower upside participation.

Do not write hypotheses as conclusions. Record parameters, robustness tests, costs, sample partitions, metrics, and selection criteria before viewing performance.

Use data only through **September 30, 2026**, and only complete periods actually available. Determine coverage from downloaded files. Do not assume factor data run through September. Set a separate primary common endpoint for each prototype, then a shared endpoint for cross-prototype contextual comparisons. Preserve all file vintages and acquisition timestamps; current downloads may contain historical revisions.

Default historical partitions:

- A: eligible observations through 2013 for historical development/context; 2014–2019 validation; 2020–latest available complete month holdout.
- B: first eligible observation–2013 for development/context; 2014–2019 validation; 2020–latest available complete month holdout.

Determine the first eligible date from real inception and warmup. Do not pad early history to manufacture these ranges. If a partition is too short, explain and replace the dates with one predetermined chronological split before examining performance. Compute rolling signals during validation/holdout from earlier available observations; do not reset history at split boundaries.

Freeze all primary rules before running the holdout. If you later change a rule after viewing holdout results, mark that period as inspected and the changed result as exploratory. Never silently reclaim it as an untouched test sample. Report a ledger of every evaluated variant, including unfavorable ones.

## 6. Project structure and reproducibility

If the user supplies an existing repository, inspect its instructions and reuse sound data/utilities. Do not overwrite unrelated work. Otherwise create a new `hw2_momentum/` project.

Use Python with small modules and one explanatory notebook per prototype. Suggested files:

```text
hw2_momentum/
  README.md
  pyproject.toml
  dependency-lock-file
  config/base.yaml
  data/raw/                 # immutable downloaded snapshots
  data/processed/           # reproducible normalized datasets
  data/manifests/           # provenance, hashes, provider metadata
  src/momentum_hw2/
    data_sources.py
    data_validation.py
    signals.py
    backtest_factor.py
    backtest_etf.py
    metrics.py
    robustness.py
    reporting.py
    cli.py
  notebooks/01_factor_overlay.ipynb
  notebooks/02_etf_dual_momentum.ipynb
  tests/
  research/
  outputs/tables/
  outputs/figures/
  outputs/audits/
  deliverables/
```

Use available stable dependencies such as pandas, NumPy, matplotlib, SciPy, statsmodels, PyYAML, requests, pytest, and a notebook runner. Use yfinance as the default Yahoo Finance adapter; verify its current API rather than assuming options or adjustment defaults. Add the Databento SDK only if authorized access is already available and useful. Pin the environment actually used. Do not install unnecessary tooling.

Expose documented commands equivalent to:

```bash
python -m momentum_hw2.cli fetch --config config/base.yaml
python -m momentum_hw2.cli validate-data --config config/base.yaml
python -m momentum_hw2.cli run --config config/base.yaml
python -m momentum_hw2.cli report --config config/base.yaml
pytest -q
```

Make the pipeline run from cached data without network access. Set a fixed seed of 9339 for resampling. Save run ID, config hash, code commit or code snapshot hash, dependency versions, input hashes, start/end dates, and warnings. Preserve sufficient raw data to reproduce the results, subject to provider licensing; do not distribute licensed Databento data if its terms do not allow it.

## 7. Data acquisition and preparation

### 7.1 Prototype A: public factor data

Acquire from Kenneth French's official Data Library:

- Monthly US Mom returns.
- Daily US Mom returns for trailing volatility and daily simulation.
- Daily and monthly Fama–French factors including `Mkt-RF` and `RF`; obtain SMB/HML for contextual regressions if readily available.
- Optional momentum-sorted portfolio returns for mechanism illustrations; they are not a substitute for security-level data.

Acquire daily VIX closing levels from Cboe's official historical-data page. Do not assume the public file's endpoint or column names; inspect the actual payload.

For every dataset, store URL/provider, download timestamp, raw filename, checksum, original units, frequency, methodology link, coverage, and known revisions. French documents a transition from legacy FIZ inputs to CIZ inputs starting with the January 2025 release. Record the downloaded methodology/vintage rather than assuming historical values or monthly aggregation remain unchanged.

Parse files deliberately:

1. Inspect archive members and descriptive headers.
2. Identify the daily or monthly block by date format and expected columns.
3. Exclude annual summary tables and footer text.
4. Convert percentages to decimal returns once and assert units.
5. Convert provider-specific missing markers to NaN; never treat missing observations as zero.
6. Sort unique dates, reject duplicates, and flag implausible extremes for review rather than clipping them.
7. Construct daily market total return as `Mkt-RF + RF`; compound total returns for the bear-state signal. Do not compound `Mkt-RF` alone and call it market total return.
8. Align available VIX observations using backward/as-of joins. Record staleness and reject unexplained gaps; do not backfill from a future observation.
9. Do not extend VIX before its real history. A long-history realized-market-volatility variant is optional and must be labeled a separate strategy.

**Critical frequency distinction:** the French daily factor's underlying portfolios are formed daily, while the monthly factor has its own documented construction. Compounding the daily factor need not reproduce the official monthly factor. Use the daily series for the main daily overlay experiment and aggregate its resulting portfolio returns to months. Present the monthly official series separately for context or a distinctly labeled monthly-only experiment. Never splice the series or treat a difference as automatically a parsing error.

### 7.2 Prototype B: ETF data

Freeze this compact primary universe before performance inspection:

| Sleeve | Instruments | Motivation |
|---|---|---|
| US equity | SPY | Broad equity exposure |
| Developed / emerging equity | EFA, EEM | Geographic breadth |
| US Treasuries | IEF, TLT | Intermediate/long duration |
| Gold / broad commodities | GLD, DBC | Different economic drivers |
| Listed real estate | VNQ | Real asset/equity-sensitive sleeve |

These tickers are design choices, not a guarantee of current liquidity or availability. Verify issuer, inception, product structure, historical coverage, and current trading status. Do not add QQQ, IWM, HYG, or other tickers after observing favorable results.

**Default: Yahoo Finance through yfinance.** The user explicitly approves Yahoo Finance. Begin with its daily ETF history rather than waiting for institutional access. Cache the provider response and record the adapter version, request options, dates, and adjustment settings. Yahoo is the source; yfinance is an independent retrieval adapter. Disclose revisions, outages, and adjustment limitations.

Implement a documented request equivalent to `yf.download(..., interval="1d", auto_adjust=False, actions=True, repair=False, keepna=True, rounding=False)` after checking the installed API. Preserve raw Close, Adj Close, Volume, dividends, and splits when returned. Specify every adjustment option rather than relying on defaults. Validate returned columns, including possible MultiIndex layouts. Do not assume every response contains Adj Close. If the API requires a per-ticker history call to obtain complete actions, use it and cache its output. Do not enable automatic repairs silently: investigate an anomaly, save original values, document any justified repair, and rerun validation.

The data cutoff is inclusive September 30, 2026. Check whether the adapter's `end` argument is exclusive; where appropriate request October 1 and explicitly filter returned trading dates to the cutoff. A successful HTTP response with empty, partial, or rate-limited content is not a successful acquisition. Use bounded retry/backoff and cached data rather than hammering the endpoint.

**Optional: Databento.** Use existing authorized access or user-supplied exports if available. Its suitability depends on the chosen dataset, coverage, venue, schema, and reference-data entitlement; do not assume its equity history spans ETF inception. Inspect provider metadata and the requested start/end dates before requesting a large range. Read a key only from a secure existing environment/configuration; never print it. The user's approval of the data source does not authorize buying data or incurring new billable usage. Use already covered access/exports; if an incremental charge is required, leave Yahoo as the working default and state the exact blocked optional request.

Databento tasks, in order:

1. Identify a relevant US equities dataset and document whether it covers consolidated trading or particular venues. Do not assume futures entitlements cover ETFs.
2. Resolve historical instrument/ticker symbology and requested dates with provider metadata.
3. Obtain a tiny covered sample using an appropriate schema such as `ohlcv-1d`, then verify session boundaries, timestamp timezone, price scaling, currency, volume units, and missing bars. A daily bar may use UTC boundaries or differ from an official closing-auction price; verify the actual definition.
4. For return-series use, obtain documented corporate-action/adjustment data where covered. Validate splits and distributions, including corrections/rescissions. Do not treat raw OHLCV returns or a split-only adjusted price as dividend-inclusive total returns.
5. When complete adjusted returns and enough history are available, compare them with Yahoo over an overlap window. Attribute material differences before deciding whether to use Databento as the primary return source. Preserve a single consistent return source per primary series; avoid an unexplained provider splice.
6. Otherwise use Databento only for execution-price checks, quotes/spreads, or liquidity diagnostics over its real coverage. Pairing Yahoo returns with Databento diagnostics is acceptable when provenance and overlap dates are explicit. Venue-level volume is not consolidated ADV; capacity calculations must name their actual volume universe.
7. Cache raw responses, request IDs/metadata where available, schema versions, and transformation steps. Prefer daily data for the homework; intraday/tick data are an optional execution check, not a reason to build a large data pipeline.

Implement CSV import for either provider as a fallback, with the same normalized schema and validation. Provider/access problems must not trigger a WRDS detour.

Required fields: date, ticker, raw close, adjusted close or verified total-return index, raw volume, and provider metadata. Corporate actions are desirable. Keep adjusted and unadjusted fields distinct.

Rules:

- Calculate returns from a validated dividend/split-adjusted total-return series. Do not add dividends again when they are already included.
- Do not fill observations before inception. Start the primary universe after all eight ETFs have usable history and all signals/warmups are ready.
- Do not create synthetic pre-inception ETFs by substituting indices in the primary test.
- Missing market-open dates need explicit diagnosis. Do not silently forward-fill unexplained data outages, rank stale assets, or liquidate an existing position because data are missing.
- Use US exchange trading dates, including actual month-end trading dates.
- Use raw close times raw share volume for dollar volume; adjusted close can distort historical traded dollars around splits.
- Reconcile several dividend dates, splits if any, and month-end returns against a second source where available.
- Report retrospective universe-selection bias and robustness to exclusions and concentration; historical eligibility alone does not remove it.

For cash use daily French `RF` or another documented realized cash return series with equivalent date coverage. Do not divide an annual yield by 252 without stating and validating that approximation. If monthly RF is the only available input, conduct a monthly experiment or label the daily disaggregation approximation; do not present it as observed daily cash returns.

### 7.3 Data-quality output

Produce `research/data_quality.md` plus machine-readable tables with counts, min/max dates, missingness, duplicate checks, inception checks, distributions, adjustment behavior, and the common analysis window. Stop an affected backtest on unresolved missing held-asset returns, broken units, or duplicate dates. Continue the other prototype when possible.

## 8. Timing convention: make execution implementable

Use a consistent daily event sequence for both minimum prototypes:

1. **Signal snapshot:** close of the penultimate trading day of each month.
2. **Decision:** after that close, using only information available then.
3. **Execution:** close of the final trading day of that month, with explicit costs.
4. **Return attribution:** old positions earn returns through execution close; new positions start earning the next trading day's close-to-close return.
5. **Next rebalance:** repeat at the following month's final trading close.

This one-trading-day information gap avoids assuming a strategy can observe final closing data and fill at that same closing price. It is a research execution approximation; a real implementation needs order deadlines and fill policy. VIX's published closing timestamp may differ from ETF equity-market close, making the gap especially useful.

Store `signal_date`, `decision_date`, `execution_date`, and `first_return_date` in every weight record. Historical data revisions are a separate limitation from timestamp leakage.

For monthly-only variants use information through the preceding month with an explicit conservative delay. Do not mix a daily executable timeline with a monthly series as if their exact timing were identical.

## 9. Prototype A: factor overlay specification

Let `m_d` be the daily French Mom spread return in decimals and `f_d` the daily RF return. Interpret unit Mom exposure as its published long–short factor notional convention; the conventional long-one/short-one interpretation implies gross exposure about 2 per unit capital. Explain the factor definition and capital convention.

At signal snapshot `s_t`, compute:

\[
\widehat\sigma_{MOM,t}=\sqrt{252}\,\operatorname{sd}(m_d: d\text{ in the latest 126 available trading days through }s_t),
\]

using sample standard deviation, `ddof=1`, and a 5% annual volatility floor for sizing. Require all 126 observations.

\[
a_t^{vol}=\min\left(1.5,\frac{0.10}{\max(\widehat\sigma_{MOM,t},0.05)}\right).
\]

Construct a market total-return index from daily `Mkt-RF + RF`. Define:

\[
Bear_t=\mathbf 1\left[TR^{MKT}(s_t)/TR^{MKT}(s_{t-24})-1<0\right],
\qquad HighVol_t=\mathbf 1[VIX(s_t)>25].
\]

Here `s_{t-24}` is the comparable signal snapshot 24 months earlier. VIX is measured in index points, so the threshold is 25, not 0.25. Define the fixed heuristic:

\[
g_t=\begin{cases}
1,&Bear_t+HighVol_t=0,\\
0.5,&Bear_t+HighVol_t=1,\\
0,&Bear_t+HighVol_t=2.
\end{cases}
\]

Run this complete attribution table:

| Variant | Factor exposure |
|---|---|
| A0 static | `a_t = 1` |
| A1 volatility-scaled | `a_t = a_t_vol` |
| A2 regime-only | `a_t = g_t` |
| A3 combined | `a_t = a_t_vol * g_t` |

Hold the selected scale through the next rebalance. Primary synthetic capital return:

\[
r_d^{capital}=f_d+a_{d-1}m_d-\text{modeled costs}_d.
\]

Also report `a*m` as the spread/excess component. The cash-plus-factor formula is a stylized funded overlay, not proof a fund can earn RF on all collateral without funding frictions. Explain financing, collateral, borrow, gross exposure, and margin assumptions; do not subtract RF again from the already excess factor component for Sharpe ratios.

Do not make a factor cumulative-return graph by blindly compounding a spread and call it fund wealth. Label the modeled capital base, cash treatment, and insolvency convention. If any modeled capital return is at or below -100%, declare ruin; no valid CAGR exists across that event. Show losses and diagnose instead of clipping or restarting wealth.

**Cost limits:** aggregate Mom has no holdings-level turnover or borrow file. Report zero-cost factor evidence explicitly as gross. An illustrative exposure-change charge can use `c * 2 * abs(a_new-a_old)` under the long-one/short-one convention, but this omits turnover inside Mom. Label it incomplete. A separate annual implementation-drag sensitivity may be shown as an assumption, never as measured full trading costs. ETF trade-cost assumptions do not make factor returns investable.

Required diagnostics: exposure path, stress-state frequency, performance by observable state, gross exposure, capped-scale frequency, and 2009 rebound-period results. Use contemporaneous market returns only for retrospective diagnosis, never in signals.

## 10. Prototype B: executable ETF strategy specification

### 10.1 Signal and selection

At each monthly snapshot `s_t`, define the 12-month total-return signal:

\[
M_{i,t}=TR_i(s_t)/TR_i(s_{t-12})-1.
\]

Use comparable monthly snapshots, not 252 trading days, for the primary lookback. For ETFs the primary signal includes the latest month; skipping it is a specified robustness test, not a default imported automatically from stock momentum.

Calculate cumulative cash return over exactly the same endpoints:

\[
C_t=\prod_{d\in(s_{t-12},s_t]}(1+f_d)-1.
\]

Rank the eight ETFs by `M`. Select the top three before applying the absolute filter; use a stable alphabetical ticker tie-break. Each selected ETF has a one-third slot. A slot is invested only if `M_i > C_t`; otherwise that slot goes to cash. Do not refill failed slots with lower-ranked assets or renormalize the survivors. Example: if two selected ETFs pass, invest one-third in each and one-third in cash.

This is a course-inspired cross-asset dual-momentum design, not an exact replication of a named author's portfolio.

### 10.2 Risk overlay

First generate the unscaled B2 strategy return history using its historical decisions. Estimate annualized trailing volatility of its daily excess returns over the latest 126 days available at `s_t`, using `ddof=1`. Require a full history, including enough additional warmup after B2 first becomes tradable.

\[
q_t=\min\left(1,\frac{0.10}{\max(\widehat\sigma_{B2,t},0.05)}\right).
\]

Multiply B2's noncash target weights by `q_t` and allocate the remainder to cash. This is a **volatility cap/de-risking rule**, not a symmetric 10% volatility target: it never leverages a low-risk portfolio to reach the target. Trailing strategy volatility can lag a change in current holdings; explain this limitation. A covariance-based forecast is optional only after the minimum is complete.

### 10.3 Required variants and benchmarks

| Variant | Rule |
|---|---|
| B0 equal-weight universe | All eight ETFs, equal target weights, monthly rebalance |
| B1 relative momentum | Top three, equal one-third weights, no absolute filter |
| B2 dual momentum | Top three slots plus absolute filter and cash |
| B3 risk-managed dual momentum | B2 risky targets multiplied by `q_t` |

Add SPY buy-and-hold, a monthly rebalanced 60% SPY / 40% IEF benchmark, and cash. Explain each benchmark and use identical dates/cash conventions. Avoid comparing raw ETF CAGR with standalone spread returns from A as if they had the same capital base or risk.

### 10.4 Daily accounting and trading costs

Between monthly rebalances let weights drift with realized returns; do not secretly rebalance daily. For a long-only portfolio, before fees:

\[
r_{p,d}=\sum_i w_{i,d-1}r_{i,d}+w_{cash,d-1}f_d.
\]

Update drifting weights using asset growth divided by portfolio growth. At the rebalance close compare new targets against these pre-trade drifted weights, not the previous month's original targets.

Define risky-asset traded notional per unit pre-trade NAV:

\[
T_t=\sum_{i\in ETF}|w^{target}_{i,t}-w^{pretrade}_{i,t}|.
\]

This counts both purchases and sales of risky ETFs and omits the offsetting cash bookkeeping entry. Charge `c*T_t`, with `c` as the cost per traded dollar. Report `T` and, if desired, the half-sum convention as a separate labeled statistic. Example: switching 100% from ETF A to ETF B creates `T=2`; 10 bps per traded dollar costs 20 bps of NAV. Initial investment from cash also incurs costs.

Primary cost assumption: **10 bps per traded dollar**, including an illustrative spread/slippage/commission allowance. Sensitivities: 0, 5, 25, and 50 bps. These are assumptions to test, not empirical estimates of current spreads. Expense ratios are generally embedded in ETF returns; do not subtract them a second time. Borrow costs are irrelevant to this unlevered long-only ETF strategy. Taxes are excluded; disclose that.

Implement costs as a consistent self-financing NAV/holdings update. Show whether targets refer to pre- or post-cost NAV; a proportional NAV haircut plus post-cost target allocation is an acceptable small-cost approximation if documented and reconciled. Include a hand-worked example. Do not spend hours building an order optimizer for this homework.

Assume fractional shares for research, with a discussion of whole-share rounding at small mandate sizes. Produce target weights, drifted weights, trades, cash balances, cost deductions, and daily/monthly returns in audit files.

## 11. Explicitly deferred work

The user does not have WRDS access. Skip WRDS/CRSP queries, account setup, entitlement checks, data-access requests, and stock-level reconstruction in this task. Databento is a market-data option for the defined prototypes; it does not automatically provide a complete point-in-time stock universe, delisting-adjusted history, sector history, or borrow availability.

The current final strategy must therefore be described using the tested factor overlays or ETF holdings. Do not call it sector-neutral stock momentum or volatility-adjusted stock selection. If useful, mention stock-level construction as one future research direction in a short roadmap; it is not a prerequisite, deliverable, or incomplete item for this run.

## 12. Verification before relying on results

Write a compact set of meaningful tests focused on costly errors:

1. **Units/parser:** a known 1% provider entry becomes 0.01; annual summaries and missing markers cannot enter daily data.
2. **Timing:** changing all returns/VIX values after a signal snapshot cannot change the decision at that snapshot.
3. **Execution:** a final-day rebalance affects returns starting the next trading day, with the old holdings earning the rebalance-day return.
4. **Eligibility:** no ETF receives a target weight before inception or before sufficient signal history.
5. **Signal:** a hand-calculated 12-month compounded return and matched cash return match code; stock skip-month indexing matches the stated endpoints if implemented.
6. **Absolute filter:** three selected slots, with one failure, produce two one-third risky allocations and one-third cash; no refill.
7. **Weights:** ETF targets and drifted holdings are nonnegative and sum to one including cash, to numeric tolerance; no leverage in B.
8. **Drift/costs:** a two-asset toy portfolio verifies drifting weights and the turnover switch example `T=2`.
9. **Cash:** all-cash returns equal the cash series before any applicable initial trade costs; zero factor exposure equals the chosen cash capital return.
10. **Risk sizing:** annualization, lagging, floor, cap, and monthly exposure persistence match manual cases.
11. **NAV reconciliation:** NAV growth matches reported daily returns after costs; wealth at/below zero is not compounded into a misleading CAGR.
12. **Run consistency:** cached reruns yield identical primary tables under the same config; two independently calculated sample periods reconcile.

Use a toy sample to demonstrate arithmetic visibly in the technical appendix. Keep notebooks as explanations calling tested modules; do not maintain a different backtest implementation inside notebooks.

## 13. Performance metrics and inference

Use daily observations for path-dependent checks and aggregate daily NAV returns to monthly returns for investor summary statistics. Explicitly distinguish monthly-end drawdown from daily drawdown. Tables must state gross/net status, date range, observations, and capital/excess-return conventions.

Report at minimum:

- CAGR: `(NAV_end/NAV_start)^(1/years)-1`, with a stated year convention; undefined after ruin.
- Annualized arithmetic mean and annualized volatility.
- Monthly Sharpe: `sqrt(12) * mean(excess_return) / sd(excess_return)`; use cash-adjusted capital returns or directly the modeled factor excess series consistently.
- Sortino using the specified monthly downside deviation relative to RF; state its denominator and annualization rather than relying on an unexplained library default.
- Maximum daily drawdown, recovery time, and whether recovery is incomplete.
- Monthly skewness and excess kurtosis, identifying the estimator.
- Worst month, worst rolling three-month period, hit rate, and cash fraction.
- Empirical monthly 95% loss VaR and expected shortfall, with sign convention and tail observation count.
- ETF average/annualized turnover, costs, average exposure, and concentration.
- Correlation and CAPM beta; contextual factor regressions where feasible.

For contextual alpha regressions, use monthly excess returns and HAC standard errors with a declared lag such as 3 months. Do not label intercepts causal alpha or a discovery of a new premium. Including Mom when regressing A's overlays is useful attribution but does not establish standalone implementability.

Estimate uncertainty with a **paired moving-block bootstrap**: 6-month blocks, 1,000 replications, fixed seed, and the same resampled blocks for compared strategies. Report 95% intervals for differences in mean excess return and Sharpe, and label assumptions/limitations. Resampling precomputed returns assesses the historical return paths; it does not re-estimate an entirely new market or eliminate strategy-selection bias. Avoid treating months as independent or emphasizing marginal p-values across many variants.

Do not normalize primary results using full-sample future volatility. If a risk-matched ex-post chart is added for illustration, label it retrospective and keep it separate from implementable results. Analyze drawdown and return differences alongside average exposure and realized volatility so that simply holding more cash is not sold as costless alpha.

## 14. Fixed robustness program

Run the primary strategy unchanged on each partition and full eligible history. Then perform one-at-a-time sensitivity tests rather than a large Cartesian grid.

### Prototype A

- Trailing factor-volatility windows: 63, **126**, 252 trading days.
- Annual risk settings: 8%, **10%**, 12%, keeping the same leverage cap.
- VIX thresholds: 20, **25**, 30 with the same bear-state structure.
- Bear lookbacks: 12, **24**, 36 months.
- Cap sensitivity: 1.0 versus **1.5**; report resulting gross exposure.
- State-only versus volatility-only versus combined overlay, already required.
- The 2008–2009 crisis/rebound and 2020 crisis/rebound, plus other worst periods found mechanically.
- Separate long-history volatility-only evidence if daily data support it; compare variants only over common dates.

### Prototype B

- Lookbacks: 6, 9, **12** months.
- Top-K: 2, **3**, 4; retain K fixed slots and send failed slots to cash.
- Latest-month included versus a clearly defined skip-month signal.
- Cost sensitivities specified above.
- Remove each ETF in turn, as a diagnostic rather than a replacement-universe search.
- Report equity and duration concentration; correlated tickers are not independent diversification.
- 2020, 2022, and mechanically selected worst strategy periods where the sample includes them.
- Execution one additional trading day later, if usable daily data permit, using the same frozen signal and correct NAV accounting.

The baseline choices in bold stay the primary choices even if an alternative wins. Save all tested variants. Leave crisis dates in primary performance; an “excluding 2009/2020” diagnostic, if added, cannot be the headline result. Do not trim adverse observations as outliers without a genuine data error.

## 15. Feasibility, costs, and capacity

For B, measure historical trailing 20-trading-day average dollar volume with lagged raw prices/volumes at each rebalance. Calculate trade dollars under illustrative AUM scenarios and participation:

\[
Participation_{i,t}=\frac{AUM_t\,|\Delta w_{i,t}|}{ADV20_{i,t}}.
\]

Use scenario starting NAVs that evolve with the backtest, or state explicitly if an illustrative constant AUM assumption is used. Show maximum and 95th-percentile participation by instrument, not just today's liquidity.

Use 1% and 5% of ADV as illustrative participation constraints to assess executable trade size; do not declare them guaranteed safe capacity. Closing-auction capacity differs from all-day ADV. Discuss auction volume availability, spreads, market impact, stressed liquidity, creation/redemption, underlying-market liquidity, and order slicing. If volumes or spreads cannot be obtained, mark the capacity conclusion provisional rather than inventing estimates.

For a proposed mandate, distinguish gross returns, modeled trading-cost returns, and optional investor returns after illustrative management fees. Any fee assumptions must be labeled. Discuss whipsaw, trend reversals, regime changes, equity overlap, duration concentration, lack of a guaranteed cash safe haven, provider risk, operational outages, and tax treatment excluded from analysis.

For A, state that public factor returns alone cannot substantiate stock-level capacity, borrow availability, or complete implementation costs. Present the extra data needed instead.

## 16. Decision rule for the final pitch

Write a comparison memo after completing both minimum prototypes. Evaluate in this order:

1. Data reliability and absence of unresolved accounting/timing defects.
2. Alignment with the investor objective and ease of explaining executable rules.
3. Net performance, downside behavior, and exposure over identical windows within each prototype.
4. Stability across chronological partitions and reasonable sensitivities.
5. Costs, liquidity, capacity assumptions, and practical implementation.
6. What can honestly be called an advantage over the proper benchmark.

Do not automatically select the highest full-sample Sharpe or present the selected strategy's holdout as unaffected by cross-strategy selection. If B3 merely reduces risk through cash, say so. If B2 is simpler and comparable after costs, it may be the stronger pitch. If no strategy demonstrates a convincing advantage, deliver a research-stage pitch with findings and a clear validation roadmap; do not promise superior performance.

## 17. Required deliverables

### 17.1 Reproducible research package

Deliver runnable source, pinned dependencies, base config, input manifest, cached normalized public data where redistribution is permitted, two executed notebooks, test report, and README. One command sequence must recreate all reported metrics and figures. Include an offline mode and CSV input instructions for blocked sources.

Required exported tables/audits:

- Daily and monthly strategy and benchmark returns.
- Monthly signals, target and pre-trade weights, cash, exposures, trades and costs.
- Performance by sample/variant and bootstrap intervals.
- Predetermined sensitivity results and the variant ledger.
- ETF participation/capacity scenarios.
- Data coverage, source map, and validation outcomes.

Store full numeric precision in CSV/Parquet; display at least five decimal places in the technical results table where appropriate. Investor slides may round for readability if exact outputs are available in the appendix.

### 17.2 Technical report

Prepare `deliverables/HW2_Momentum_Research_Report.md` and a shareable PDF if supported. Include:

1. First-page executive summary: objective, final rules, measured findings, main caveat.
2. Landscape and literature connection.
3. Data provenance, adjustments, coverage, vintage, and biases.
4. Definitions, equations, timing, accounting, and a worked example.
5. Primary results and component attribution.
6. Robustness and uncertainty.
7. Execution feasibility, costs, capacity, and investor suitability.
8. Limitations, risks, and what would change the conclusion.
9. Investor Q&A and references.

Keep writing academic, clear, and informative. Explain why each design choice exists and what the results show. Hanyu should be able to reproduce the strategy and answer questions independently.

### 17.3 Investor presentation

Build an editable PowerPoint deck and PDF when presentation tools are available; otherwise provide a complete slide manuscript with figures and speaker notes, explicitly naming the missing format. Read the relevant presentation/PDF skills in your environment before creating those artifacts.

Target **12 substantive slides plus technical appendix**; this is a suggested structure, not an instructor-imposed length:

| Slide | Content |
|---|---|
| 1 | Strategy name, raising-assets objective, summary, illustrative mandate |
| 2 | Investor problem and momentum strategy landscape |
| 3 | Economic mechanism and course/literature connection |
| 4 | Exact strategy rules with a worked holdings example |
| 5 | Risk management and what it can/cannot address |
| 6 | Data, sample, timing, and evaluation design |
| 7 | Net results versus proper benchmarks, with dates/costs |
| 8 | Equity curves, drawdowns, and component attribution |
| 9 | Robustness, historical holdout, and uncertainty |
| 10 | Costs, liquidity, capacity, and proposed implementation |
| 11 | Competitive advantages supported by evidence and principal risks |
| 12 | Investor Q&A, next validation step, and clear proposed mandate |

Appendix: full equations, exact metrics, methodology, variant ledger, stress cases, statistical conventions, sources, and reproduction instructions. Include concise speaker notes. Use professional monochrome or restrained visual styling and legible charts; include return basis, sample dates, and cost assumptions on relevant slides. Render and inspect every slide/page for clipping, unreadable text, and inconsistent numbers.

Minimum figures: NAV curves on comparable capital conventions, daily drawdowns, regime/exposure path for A, cash/risky allocation history for B, component comparison, and a modest robustness display. Use actual computed data. Do not create fictional favorable curves, decorative charts, or anonymous performance numbers.

### 17.4 Investor questions to answer directly

- Why might momentum persist, and why does this particular design fit the objective?
- Which components are established and what, if anything, is your contribution?
- How does this differ from buy-and-hold, a momentum ETF, and futures trend following?
- Is the reduction in drawdown just a consequence of holding less risk?
- When does the strategy lose money or fail to participate in gains?
- What happens during a fast rebound, a range-bound market, or simultaneous stock/bond weakness?
- How were ETFs, parameters, and dates selected, and how many variants were tried?
- Which evidence is historical validation versus genuinely future evidence?
- What costs, funding assumptions, taxes, and data limitations are excluded?
- How much capital can reasonably be traded, and what evidence supports that estimate?
- What would invalidate the strategy or warrant shutting it down?
- What operational action follows a missing data feed or failed rebalance?

For operational contingencies, propose preserving existing holdings pending verified data and escalating the issue; do not invent returns or silently change the strategy in the historical backtest.

## 18. Base configuration template

Create a machine-readable config equivalent to this. Adapt implementation keys as necessary, but preserve the research defaults and record deviations.

```yaml
project: fincb9339_hw2_momentum
research_seed: 9339
data_cutoff: "2026-09-30"
pitch_objective: raise_assets
data_sources:
  factor: kenneth_french
  vix: cboe
  etf_primary: yahoo_finance
  etf_adapter: yfinance
  etf_secondary_optional: databento
  yahoo_auto_adjust: false
  yahoo_actions: true
  yahoo_repair: false
  wrds_enabled: false
  new_billable_data_usage_authorized: false
timing:
  signal: penultimate_trading_day_close
  execution: final_trading_day_close
  new_holdings_first_return: next_trading_day
factor:
  primary_frequency: daily
  volatility_days: 126
  target_annual_volatility: 0.10
  annual_volatility_floor: 0.05
  scale_cap: 1.5
  bear_lookback_months: 24
  vix_threshold_points: 25
  stress_scales: [1.0, 0.5, 0.0]
  cost_status: gross_plus_separately_labeled_sensitivities
etf:
  tickers: [SPY, EFA, EEM, IEF, TLT, GLD, DBC, VNQ]
  universe_policy: fixed_universe_common_history
  lookback_months: 12
  skip_latest_month: false
  top_k: 3
  failed_slot_destination: cash
  tie_break: ticker_alphabetical
  weight_method: equal_slots
  volatility_days: 126
  risk_cap_annual_volatility: 0.10
  annual_volatility_floor: 0.05
  risk_scale_cap: 1.0
  cost_bps_per_traded_dollar: 10
  cost_sensitivity_bps: [0, 5, 25, 50]
  fractional_shares: true
  leverage_allowed: false
validation:
  development_end: "2013-12-31"
  validation_end: "2019-12-31"
  historical_holdout_start: "2020-01-01"
  bootstrap_block_months: 6
  bootstrap_replications: 1000
capacity:
  initial_aum_usd: [1000000, 10000000, 50000000]
  adv_days: 20
  illustrative_adv_participation_limits: [0.01, 0.05]
```

## 19. Starting source links

These are discovery/methodology pages, not permission to assume coverage, schema, or entitlement. Verify download links and data definitions at execution time and cite actual accessed sources in the final work.

- Kenneth French Data Library: <https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html>
- Monthly Mom definition: <https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor.html>
- Daily Mom definition: <https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor_daily.html>
- CRSP/French data changes: <https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/changes_crsp.html>
- Cboe VIX historical data: <https://www.cboe.com/tradable_products/vix/vix_historical_data>
- yfinance download API: <https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html>
- yfinance history API: <https://ranaroussi.github.io/yfinance/reference/yfinance.price_history.html>
- Databento documentation: <https://databento.com/docs>
- Databento adjustment-factor examples: <https://databento.com/docs/examples/adjustment-factors/applying-adjustment-factors>
- Databento adjustment-factor specification: <https://databento.com/docs/venues-and-datasets/adjustment-factors>

Maintain `research/source_map.md`: claim/formula, uploaded filename and page/section if recoverable, exact local excerpt location, outside URL if used, and access date. Clearly separate a paper's historical results from your reproduced results and from your untested hypotheses. Do not cite this specification as original evidence.

## 20. Acceptance checklist and final handoff

Mark each item PASS, FAIL, or BLOCKED with its evidence:

- [ ] All assignment requirements map to final content.
- [ ] Yahoo defaults and Databento coverage/adjustments are documented if that optional source was used.
- [ ] No WRDS work was attempted or required.
- [ ] Both minimum prototypes executed, or a precise data/access blocker is documented.
- [ ] Research defaults were frozen and deviations/inspected holdouts disclosed.
- [ ] Data provenance, units, adjustment conventions, and vintage are recorded.
- [ ] No unexplained missing held-asset returns, pre-inception weights, or timing leakage.
- [ ] Factor daily/monthly construction and capital conventions are correctly labeled.
- [ ] ETF holdings drift, cash earns documented returns, and turnover/costs reconcile.
- [ ] Primary comparisons use matching dates and appropriate benchmarks.
- [ ] Gross versus net evidence and measured versus assumed costs are explicit.
- [ ] Robustness includes adverse variants and chronological validation.
- [ ] Uncertainty is reported without overstating statistical or practical significance.
- [ ] Capacity claims are tied to data or marked provisional.
- [ ] Every headline number traces to a reproducible output.
- [ ] Report explains formulas and main steps, including a worked example.
- [ ] Presentation and PDF were rendered and visually inspected if generated.
- [ ] A cached clean run reproduces reported results and tests pass.
- [ ] Final deliverables are saved durably using the environment's artifact workflow.

Your final response must state what was completed, the selected pitch design and why, the actual sample dates, the most decision-relevant measured findings, the principal limitations, verification status, and links to the deliverables. If a blocker remains, name the exact required input and include the completed unblocked work. Do not claim the strategy is validated for live capital, automatically submit the homework, or end with an offer to do steps that this specification already authorized.
