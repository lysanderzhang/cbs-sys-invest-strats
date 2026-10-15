# Investor presentation: 12 substantive slides + appendix

## 1. Cross-asset dual momentum

Raising assets for a transparent monthly ETF portfolio
Research-stage B3: risk cap, explicit cash, no leverage
CAGR 6.89% | daily max drawdown -17.91%
Illustrative USD 10 million mandate; execution validation starts with a USD 1 million scenario

Speaker notes: ETF capital: 2007-08-31 execution inception to 2026-08-31; modeled net 10 bps/traded dollar. Objective is raising assets, not working capital. Performance is historical and mixed; no live readiness. Hanyu Zhang, FINCB9339 Homework 2.

## 2. Momentum strategy landscape

Buy-and-hold: continuous market exposure
Relative momentum: rank assets against peers
Absolute momentum: compare an asset with its cash hurdle
Our dual design: three selected ETF slots, failed slots to cash
Futures CTAs can short declining markets; this portfolio cannot

Speaker notes: Lecture slides 4-7, 22-23, 42-44; Asness et al. 2014 pp 2-4. Stock momentum ETFs rank stocks within equities. Eight tickers do not equal eight independent exposures.

## 3. Economic mechanism and contribution

Published hypotheses: delayed information, feedback and risk premia
Equity factor crashes: past losers rebound after panic states
ETF long/cash risks differ from short-loser equity momentum
Contribution: controlled comparisons with reproducible timing and accounting

Speaker notes: Daniel & Moskowitz 2016 introduction pp 221-223; Asness et al. 2014 Myth 10; Kolanovic & Wei 2015 pp 19-20. Published findings are motivation, not our measured returns. No new anomaly, sector neutrality or conditional-mean replication claimed.

## 4. Exact monthly holdings rule

Universe: SPY EFA EEM IEF TLT GLD DBC VNQ
Rank 12-month total returns; choose top 3
Each 1/3 slot invests only if its return exceeds matched cash
Example signals 12%, 8%, 1%; cash 2% -> two 1/3 ETFs +1/3 cash
Vol 16% -> q 0.625 ->20.83%, 20.83%, 58.33% cash

Speaker notes: Signals use comparable penultimate monthly snapshots, not 252 days. Alphabetical tie break. No refill or renormalization. Worked numbers here are illustrative arithmetic, not historical signals. Actual decisions and endpoints are in etf_signals.csv; see notebook 2.

## 5. Risk cap and opportunity cost

B3 estimates 126-day gross B2 excess volatility
q=min(1, 10%/max(volatility, 5%)); remainder cash
Average cash 22.82% versus B2 5.22%
Protection reduces upside and does not guarantee maximum loss

Figure: ../../results/figures/B_allocations.png

Speaker notes: Forecast is trailing strategy volatility, not a current-holdings covariance forecast. Monthly decisions persist; weights drift. B3 never leverages to reach 10%. Baltas & Kosowski 2013 section 3 motivates volatility normalization, but futures positions and estimator differ.

## 6. Data, timing and historical validation

Real French, Cboe and Yahoo/yfinance snapshots
September cutoff; French RF/Mom available only through August
Signal penultimate close -> execute final close -> next-session return
All 8 ETF history begins 2006; B3 warmup -> September 2007 returns
Development to 2013 | validation 2014-19 | historical holdout 2020-26

Speaker notes: ETF first common execution 2007-08-31; first invested return 2007-09-04. Factor first execution 1990-01-31; first return 1990-02-01. RF cash endpoints bind August 31. Adj Close includes distributions; no double counting. Current vintages may revise history. Holdout is publicly known and inspected.

## 7. Modeled net results versus benchmarks

B0: CAGR 6.40% | Sharpe 0.487 | max DD -37.92%
B1: CAGR 8.66% | Sharpe 0.607 | max DD -25.12%
B2: CAGR 7.95% | Sharpe 0.570 | max DD -25.15%
B3: CAGR 6.89% | Sharpe 0.614 | max DD -17.91%
60_40: CAGR 8.16% | Sharpe 0.719 | max DD -32.62%
SPY: CAGR 11.08% | Sharpe 0.662 | max DD -55.19%

Speaker notes: ETF capital: 2007-08-31 execution inception to 2026-08-31; modeled net 10 bps/traded dollar. Sharpe is monthly cash-adjusted, ddof 1. Drawdown is daily;60/40 rebalances monthly. Initial order costs included. Benchmark 60/40 has higher full-history Sharpe than B3. See performance.csv for five-decimal output.

## 8. Lower drawdown comes with lower return

Relative selection improves historical return over equal weighting
Absolute filter scarcely improves worst drawdown here
Volatility cap provides the strongest ETF drawdown reduction
B3 trails SPY and 60/40 in full-history CAGR

Figure: ../../results/figures/B_nav_drawdown.png

Speaker notes: ETF capital: 2007-08-31 execution inception to 2026-08-31; modeled net 10 bps/traded dollar. Comparing component risks and mean exposures prevents presenting lower cash-adjusted risk as costless alpha. B1 CAGR8.66%, B2 7.95%, B3 6.89%; values trace to performance.csv.

## 9. Robustness and uncertainty

Historical holdout B3: CAGR 10.46% | Sharpe 0.805
B3-minus 60/40 Sharpe 95% CI: [-0.598, 0.279]
Skip-month diagnostic worsens drawdown; gold exclusion hurts
All 84 ledger rows retained; stronger 9-month result is not adopted

Figure: ../../results/figures/B_robustness.png

Speaker notes: 1000 paired moving-block draws, 6-month blocks, seed 9339. No future out-of-sample claim; cross-strategy selection inspected holdout. Sensitivity common start 2007-10-31 accommodates skip-month warmup. CI includes zero; resampling historical returns does not remove selection bias.

## 10. Costs, liquidity and mandate size

B3 turnover 3.15x NAV/year; assumed 10 bps per dollar
1m/10m/50m AUM scenarios evolve with net NAV
10m B3 maximum DBC participation 19.17% of lagged ADV20
All-day vendor ADV does not certify closing-auction capacity
Validate 1m scenario first;10m single-close fills are not established

Speaker notes: Participation from raw Close*Volume through snapshot, abs delta weights, pretrade evolving NAV. Cost is an assumption, not measured spread.1%/5% ADV are illustrative constraints. Auction/impact/underlying liquidity and independent data checks needed. Taxes and investor fees excluded.

## 11. Evidence-supported advantages and risks

Advantages: explicit holdings, fixed rules, no leverage, cash audit
B3 reduced losses in 2022; it missed upside in 2020
Risks: whipsaw, reversals, gold dependence and duration overlap
Higher full-sample Sharpe than 60/40 is not demonstrated

Speaker notes: 2020 B3 return 7.77% vs 60/40 15.99%;2022 B3 -5.03% vs 60/40 -16.67%. Daily exposure/cost files substantiate implementation transparency. This is a design advantage, not a claim of statistical alpha. Provider revisions and retrospective universe selection remain.

## 12. Proposed research mandate and investor Q&A

Proposal: B3 research-stage risk-limited ETF design
Why more cash? It buys lower exposure and sacrifices return
Why not B1? Keep it as the higher-return comparator
Next milestone: independent data, auction costs, prospective paper signals
Feed failure: preserve holdings, verify data, escalate and log

Speaker notes: Raising assets remains the objective, with illustrative 10m contingent on evidence. No trades or assignment submission authorized. Suspend new decisions after material data/accounting defects, repeated operational failures or participation breaches; do not retrofit these rules into historical returns. Full investor Q&A is in report section 9.

## 13. Appendix | Factor experiment

A0 gross synthetic CAGR 7.94% | drawdown -63.29%
A3 gross synthetic CAGR 11.99% | drawdown -18.89%
Bear 24 months + VIX>25 -> exposure 0 when both flags
RF + a*Mom: funding/borrow/internal turnover not measured

Figure: ../../results/figures/A_nav_drawdown.png

Speaker notes: A dates 1990-01-31 to 2026-08-31. French Mom six size/momentum portfolios, daily formed daily; monthly official series separate. Unit factor gross notional 2, cap 1.5 permits gross 3. A is not an executable stock strategy. Daniel-Moskowitz conditional mean/variance sizing is not replicated.

## 14. Appendix | Factor exposures and panic states

A0=1 | A1=vol scale | A2=state scale | A3=combined
a_vol=min(1.5, 10%/max(sigma 126, 5%))
Market total return compounds Mkt-RF + RF
Published loser-rebound mechanism motivates the fixed heuristic

Figure: ../../results/figures/A_exposure_regime.png

Speaker notes: Signals use past 24 comparable monthly snapshots and backward VIX. Exposure decisions held after execution; neither VIX nor market rebound from future periods enters signal. March-May 2009 static capital loses 45.64%; zero factor exposure avoids it in A2/A3. Internal Mom turnover, financing and borrow omitted.

## 15. Appendix | Accounting and statistical conventions

Daily weights drift; rebalance only at execution close
T=sum risky |target-pretrade|; full A-to-B switch T=2
NAV_after=NAV_before*(1+gross)*(1-0.001*T)
Sharpe=sqrt(12)*mean(monthly excess)/sample_sd
CAGR ACT/365.25 | HAC3 | downside RMS Sortino

Speaker notes: Worked 50/50 drift example in report section 4 and tests. Targets are post-cost allocations using proportional NAV haircut. Initial execution charge combined into first holding month. Cash is compounded daily RF; empirical monthly VaR/ES loss-positive with tail count. Undefined Sharpe for deterministic excess cash.

## 16. Appendix | Exact component evidence

Decimals to five places; ETF modeled net, factor synthetic gross
A0: CAGR 0.07938; Sharpe 0.39282; DD -0.63288
A1: CAGR 0.11762; Sharpe 0.75071; DD -0.24129
A2: CAGR 0.10500; Sharpe 0.70178; DD -0.26873
A3: CAGR 0.11994; Sharpe 0.89354; DD -0.18893
B0: CAGR 0.06405; Sharpe 0.48708; DD -0.37924
B1: CAGR 0.08658; Sharpe 0.60665; DD -0.25123
B2: CAGR 0.07953; Sharpe 0.57005; DD -0.25147
B3: CAGR 0.06891; Sharpe 0.61357; DD -0.17911

Speaker notes: Full numeric precision, dates, gross/net basis, costs and exposures are exported in performance.csv. Tables are reproducible, not hand-entered. Additional SPY/60-40 benchmarks are on slide 7 and in CSV.

## 17. Appendix | Sources and reproduction

Course lecture Momentum; Homework 2 handout
Daniel-Moskowitz 2016; Asness et al. 2014
Kolanovic-Wei 2015; Baltas-Kosowski supplied 2013 version
French official library | Cboe VIX | Yahoo via yfinance 1.7.0
README: cached run, tests, reports and executed notebooks

Speaker notes: Exact paths/pages/lines and URLs: research/source_map.md. Cached inputs/manifests record acquired UTC timestamps, SHA256 and options. Run python -m momentum_hw 2.cli validate-data --offline; pytest; run --offline; report --offline. No WRDS, new charges, publishing or submission.

