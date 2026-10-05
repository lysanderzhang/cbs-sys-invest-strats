# HW2 Momentum Research Report

Hanyu Zhang | FINCB9339 | October 4, 2026

## Executive summary

Objective: raise assets for a transparent monthly cross-asset ETF portfolio. The default illustrative USD 10 million mandate is a research scenario, not a capacity commitment. Recommend B3 as a research-stage risk-limited portfolio, with a USD 1 million execution-validation scenario before considering USD 10 million. No live-capital readiness or superior-return promise is established.

On the identical ETF capital window 2007-08-31 to 2026-08-31 (first invested return 2007-09-04), B3 modeled net CAGR is 6.89%, monthly Sharpe 0.61357, and maximum daily drawdown -17.91%. B1 achieves 8.66% CAGR; monthly 60/40 achieves 8.16% and Sharpe 0.71919. B3 has 22.82% average cash, versus 5.22% for B2. Downside improvement comes with lower risky exposure and lower returns.

The B3-minus-60/40 paired six-month bootstrap Sharpe difference is -0.10562, 95% interval [-0.59792, 0.27882]. This does not establish superiority. Historical holdout B3 CAGR is 10.46%, Sharpe 0.80501; these dates are publicly known, and cross-strategy selection inspected them.

The distinct factor experiment runs 1990-01-31 to 2026-08-31, first return 1990-02-01. A3 synthetic cash-plus-Mom gross CAGR is 11.99%, versus 7.94% static; maximum daily drawdowns are -18.89% versus -63.29%. These are aggregate factor exposure experiments with incomplete funding/borrow/cost assumptions, not executable stock portfolios.

French RF/Mom stop in August 2026; September ETF/VIX data are cached but unused. Capacity is provisional: the evolving USD 10 million B3 scenario reaches 19.17% of ADV20 for DBC. A single close cannot be justified from all-day vendor volume alone.

## 1. Landscape and published research

The instructor uses time-series/absolute momentum for an asset's own past performance and cross-sectional/relative momentum for rankings across assets. Dual momentum combines the two. Buy-and-hold retains market exposure; a stock momentum ETF ranks securities within equities; diversified futures trend following can short falling markets and normalize instrument risk. Our B ranks eight US-listed ETFs, is long-only, and routes failed slots to cash. It cannot profit directly from shorting a persistent decline.

The lecture's dual momentum modules use 12 months including the latest month and a cash hurdle. B adopts these concepts but uses three fixed slots across a different eight-ETF universe. It is not a replication of the four-module permanent portfolio. Equal slots are capital weighting, not equal marginal volatility (EMV).

Daniel and Moskowitz, Momentum crashes (2016), describe panic states after market declines and high ex-ante volatility, with past losers rebounding strongly. Their conditional-mean/variance strategy differs from our fixed bear/VIX heuristic and inverse-volatility overlay. Their published improvements are not our results. Their decile WML construction also differs from French's six size/momentum portfolios. Lecture slides 65-88 explain these mechanisms. Some extracted equations have scrambled two-column text; no ambiguous extracted formula was coded.

Asness et al., Fact, Fiction and Momentum Investing (2014), discuss broad evidence, implementation, costs and diversification with value. Their long-run stock results, institutional trading-cost evidence and tax findings do not validate this ETF design. Their argument for simple definitions motivates frozen parameters and retaining adverse periods.

Kolanovic and Wei (2015), pp 19-20 and 59-60, distinguish absolute versus relative signals, use a one-business-day information gap, and show that portfolio volatility targeting is not invariably beneficial. Their VIX threshold 25 example motivates one part of A but is not the same combined rule. Baltas and Kosowski (supplied January 2013 version), section 3, use signed futures trends and inverse-volatility normalization; they study frequencies and futures/CTA capacity. Those results cannot be transferred to our eight ETFs. Contribution: a transparent controlled implementation and audit trail, not a new anomaly.

## 2. Data, coverage and biases

Inputs are real downloaded snapshots. Kenneth French official daily/monthly US Mom and Fama-French market/RF/SMB/HML archives; Cboe official VIX closing levels; Yahoo Finance through yfinance 1.7.0. Request options explicitly preserve Close, Adj Close, Volume and actions: auto_adjust=False, back_adjust=False, actions=True, repair=False, keepna=True, rounding=False, prepost=False; end 2026-10-01 is exclusive, and records are filtered through September 30. Filenames, timestamps, SHA256, adapter signature/options, units, coverage and original headers are in data/manifests.

French daily Mom coverage 1926-11-03 to 2026-08-31, monthly Mom 1927-01 to 2026-08. VIX starts 1990-01-02 and reaches cutoff. ETF observations begin SPY 1993-01-29, EFA 2001-08-27, EEM 2003-04-14, IEF/TLT 2002-07-30, GLD 2004-11-18, DBC 2006-02-06, VNQ 2004-09-29, and all reach 2026-09-30. Issuer inception dates can precede first vendor observations; no missing early days are manufactured. DBC binds common price history. All actual analysis sessions match the French market calendar with no missing prices.

Percent factor entries are divided by 100 once; missing markers become NaN; only date-shaped daily/monthly blocks are parsed, excluding annual summaries. VIX is joined backward, source dates/staleness exported, with gaps over 7 calendar days rejected. Two >20% EEM daily gains in October 2008 are flagged and retained as crisis observations; they were not clipped or removed. Independent validation of these extremes remains a data-risk limitation.

Adj Close is the vendor total-return proxy; dividends are not added again. Internal dividend-date comparisons are exported, not called independent-source verification. Close/Volume conventions and distribution revisions remain provider risks. EFA2005 and EEM2005/2008 split events are preserved and included in internal return checks. Yahoo Close is already split-normalized, not an original pre-split transaction price. Close times vendor Volume is a dollar-volume proxy; historical volume normalization remains uncertified, strengthening the provisional capacity limitation. Targeted issuer/venue action checks are in research/corporate_actions.md; full independent price and month-end return validation remains unavailable. Volume capacity uses reported Close times daily share Volume, not Adj Close. The eight-ticker retrospective universe choice creates selection/survivorship risk even with proper inception timing. ETF expenses are embedded in returns, not deducted again; tax, fee and execution assumptions are separate.

French transitioned from legacy FIZ to CIZ with the January 2025 release; this current snapshot can revise old observations. Daily Mom's underlying portfolios are formed daily; official monthly Mom is formed monthly. We do not splice them, and daily-derived capital returns need not match official monthly spread returns. No WRDS/CRSP query or stock reconstruction was attempted. Databento was unused and no data fees incurred. Cached public inputs are for authorized personal academic use; public redistribution rights are not presumed.

## 3. Equations and timing

Let m_d denote daily French Mom and f_d daily RF. French Mom =0.5(Small High + Big High)-0.5(Small Low + Big Low), using six value-weight portfolios from size and prior-return sorts. Unit factor exposure has conventional long-one/short-one gross notional about 2 per modeled dollar of capital. Our daily synthetic capital return r_d=f_d+a_previous*m_d-cost_d. The factor spread is already an excess component; do not subtract RF a second time. RF on collateral, financing, margin and stock borrowing are stylized; factor-return data cannot establish stock capacity or sector neutrality.

At penultimate trading close s_t, sigma_t=sqrt(252)*sample_sd(last 126 Mom daily returns), ddof=1. Volatility exposure a_vol=min(1.5, 0.10/max(sigma_t, 0.05)). Market TR compounds Mkt-RF+RF. Bear=1[market_TR(s_t)/market_TR(s_(t-24))-1<0]. HighVol=1[VIX(s_t)>25 index points]. State scale g equals 1 with neither flag, 0.5 with one, 0 with both. A0=1; A1=a_vol; A2=g; A3=a_vol*g. Exposure is held until next monthly execution. A is gross; illustrative change charges 2*abs(delta a)*cost and annual exposure drags omit internal stock turnover and borrow.

For ETF i, M_i=AdjClose_i(s_t)/AdjClose_i(s_(t-12))-1. Cash hurdle C=product(1+RF_d)-1 over exactly (s_(t-12), s_t]. Rank all eight by descending M, alphabetical ties; top 3 each receive 1/3 slots. B1 invests each slot. B2 invests only if M_i>C; failed slots remain cash, without refill or survivor renormalization. B0 resets equal 1/8 monthly. SPY benchmark holds after initial trade;60/40 resets SPY60%, IEF40% monthly; cash earns observed RF.

B3 first requires 126 days of the historical unscaled gross B2 strategy's daily excess path after B2 starts trading. q=min(1, 0.10/max(sqrt(252)*sd(B2 excess 126), 0.05)). Multiply B2 risky targets by q; allocate the balance to cash. It is a volatility cap, never leverage to hit 10%. Forecast uses past strategy returns, so can lag changes in holdings or covariance. The primary common start includes this extra warmup; all benchmarks begin from cash on that same date.

Decision after penultimate close; execute final close with old holdings earning the execution-day return; new holdings earn from the following session. Signal/decision/execution/first-return fields are exported. Signals compare monthly snapshots, not 252 days. VIX publishing time and foreign underlying markets may differ from equity close; the one-session gap is conservative but not a fill guarantee. An additional-session delay diagnostic preserves the original snapshot.

Weights drift daily: gross return=sum(w_previous*r_asset)+w_cash*RF; pretrade weight_i=w_previous_i*(1+r_i)/(1+gross). Risky turnover T=sum_i|target_i-pretrade_i| excludes cash but counts both buys and sells. Cost fraction=c*T, c=0.001 (10 bps). NAV_after=NAV_before*(1+gross)*(1-c*T); allocate post-cost NAV at target weights. This proportional haircut is the specified approximation; realized trade dollars differ slightly from the pre-cost notional used to size costs. Initial investments incur charges. No daily rebalance or hidden leverage. If return<=-100% or NAV<=0, halt and declare ruin; no clipping or restart.

Initial close has no prior invested return. Its initial charge is stored on execution day in daily accounting and combined into the first full holding month's return for monthly statistics, preserving cumulative wealth. ACT/365.25 CAGR uses inclusive elapsed calendar days from initial execution. Partitions use actual inherited returns without resetting signal history. All primary comparisons within each prototype use identical dates; cross-prototype headline CAGR comparisons are inappropriate because investability/capital conventions differ.

## 4. Worked examples and intermediate steps

Arithmetic example (illustrative, not empirical performance): at a snapshot selected ETF signals are 12%, 8%, 1%; matched cash is 2%. Relative selection gives 1/3 to each. Absolute filtering keeps the first two and sends the third 1/3 to cash. If forecast B2 volatility is 16%, q=10%/16%=0.625; B3 targets are 0.20833333, 0.20833333, 0 cash-failed risky slot, and 0.58333333 cash. No lower-ranked asset replaces the failure.

Drift example: start with 50% A, 50% B; A returns 10%, B0%. Gross NAV rises 1.05; weights become 0.55/1.05=0.52380952 and 0.50/1.05=0.47619048. Target 100% B gives T=|0-0.52380952|+|1-0.47619048|=1.04761905. At 10 bps, cost fraction 0.00104762. Post-cost NAV=1.05*(1-0.00104761905)=1.04890000, then allocate B100%. A full 100% A-to-B switch has T=2 and 20 bps cost, not 10 bps.

Reproduction of a real decision: open outputs/audits/etf_signals.csv, filter the desired execution_date, and verify lookback_start/end against processed/etf_adjclose.csv; compare the matched cash index from etf_cash.csv. Then verify B3 q in etf_risk_sizing.csv and targets/trades/holdings. The notebooks print an actual eligible row and reproduce its endpoints. Unit tests implement the worked arithmetic; actual-path audits independently reconcile trades, return weights and NAV.

Monthly return=product daily NAV growth factors-1. Monthly excess=capital monthly return-compounded daily cash. Sharpe=sqrt(12)*mean(excess)/sample_sd(excess). Sortino=sqrt(12)*mean(excess)/sqrt(mean(min(excess, 0)^2)), including all months in the downside denominator. Annual arithmetic mean=12*mean(monthly capital returns); annual volatility=sqrt(12)*sample_sd(monthly capital returns). Sample adjusted skewness and Fisher excess kurtosis use pandas estimators. VaR95 is minus 5th-percentile monthly capital return; ES averages returns at/below that cutoff, with tail_n. Daily maximum drawdown uses prior peak including initial NAV1; recovery reports peak-to-recovery calendar days or elapsed unrecovered duration. Daily and monthly-end drawdowns are separate columns.

## 5. Primary measured results and attribution

Exact decimal return statistics appear below (five decimals); all full-precision outputs are CSV. Factor rows are synthetic gross; ETF rows use 10 bps assumed traded-dollar costs. Dates: A 1990-01-31 to 2026-08-31; B 2007-08-31 to 2026-08-31. Initial execution charge enters the first holding month, not an artificial partial month.

A3 lowers drawdown from-63.29% to-18.89% and realized annual monthly capital volatility from 16.17% to 10.45%. Average factor exposure falls to 0.88869, with dynamic timing as well as volatility management; these controls cannot guarantee future crash avoidance. March-May 2009 gross static synthetic capital loses 45.64%, while the regime/combined experiments sit at zero factor exposure and earn the period's zero recorded RF. That is avoidance through de-risking, not a stock hedge replication. Exposure diagnostics retain both-stress and cap frequencies.

ETF relative selection B1 increases full-sample CAGR from equal weight 6.40% to 8.66% but portfolio concentration and whipsaw remain. B2 absolute filtering reduces CAGR to 7.95% and barely changes worst full-history drawdown (-25.12% versus-25.15%). The downside hypothesis is not uniformly supported. B3 reduces the drawdown to-17.91% and volatility to 9.26%, with average cash 22.82%; CAGR declines to 6.89%. This is a paid risk reduction.60/40 has higher full-sample Sharpe (0.71919 versus 0.61357), and SPY has higher CAGR11.08% with deeper drawdowns. We do not select solely by Sharpe.

2020 B3 returns 7.77%, B2/B1 10.22%, 60/40 15.99%, SPY18.33%: the lower-risk design misses upside.2022 B3 loses 5.03%, B2 9.45%, 60/40 16.67%, SPY18.18%: the cap helps but does not eliminate simultaneous stock/bond weakness. Crisis-specific returns are descriptive and retained inside all primary metrics. Regressions use monthly excess, CAPM and contextual market/SMB/HML attribution with HAC3 standard errors; A additionally includes daily-derived static factor capital excess. Intercepts are not causal alpha or proof of a new premium; omitted bond/gold exposures can matter for B.

| variant   | basis                              |    CAGR |   annual_vol |    Sharpe |   max_daily_drawdown |   average_exposure |
|:----------|:-----------------------------------|--------:|-------------:|----------:|---------------------:|-------------------:|
| A0        | synthetic cash-plus-factor gross   | 0.07938 |      0.16174 |   0.39282 |             -0.63288 |            1.00000 |
| A1        | synthetic cash-plus-factor gross   | 0.11762 |      0.12442 |   0.75071 |             -0.24129 |            0.98762 |
| A2        | synthetic cash-plus-factor gross   | 0.10500 |      0.11476 |   0.70178 |             -0.26873 |            0.84122 |
| A3        | synthetic cash-plus-factor gross   | 0.11994 |      0.10450 |   0.89354 |             -0.18893 |            0.88869 |
| B0        | modeled net 10bps per risky dollar | 0.06405 |      0.11092 |   0.48708 |             -0.37924 |            1.00000 |
| B1        | modeled net 10bps per risky dollar | 0.08658 |      0.12729 |   0.60665 |             -0.25123 |            1.00000 |
| B2        | modeled net 10bps per risky dollar | 0.07953 |      0.12294 |   0.57005 |             -0.25147 |            0.94783 |
| SPY       | modeled net 10bps per risky dollar | 0.11077 |      0.15583 |   0.66228 |             -0.55189 |            1.00000 |
| 60_40     | modeled net 10bps per risky dollar | 0.08165 |      0.09559 |   0.71919 |             -0.32617 |            1.00000 |
| CASH      | modeled net 10bps per risky dollar | 0.01451 |      0.00569 | nan       |              0.00000 |            0.00000 |
| B3        | modeled net 10bps per risky dollar | 0.06891 |      0.09264 |   0.61357 |             -0.17911 |            0.77175 |

## 6. Robustness and uncertainty

Primary rules were frozen before downloaded performance was viewed. Development through 2013, validation 2014-2019, historical holdout 2020-2026-08-31; histories carry across boundaries. Holdout is public historical evidence, not unseen future performance. Recommendation across variants uses those inspected outcomes; selection uncertainty persists. The variant ledger has 84 evaluated rows, including gross attribution, adverse sensitivities and incomplete factor costs. No winning alternative replaced the frozen parameters.

B3 holdout CAGR10.46%, Sharpe 0.80501; B1 holdout CAGR12.97%, Sharpe 0.80375. B3 improves full-sample Sharpe versus B2 by 0.04352, but its 95% block-bootstrap interval [-0.06125, 0.16253] includes zero. Its comparison with 60/40 likewise includes zero. Uncertainty does not support a guaranteed advantage.

Paired moving-block bootstrap uses 6-month noncircular overlapping blocks, 1000 replications, seed 9339, identical indices for compared strategies; report annualized mean-excess differences and Sharpe differences. This resamples precomputed historical paths, not new signals/markets, does not remove universe/parameter selection bias, and has limited crisis-tail observations. HAC3 regressions are contextual, and multiple variants do not create independent discoveries.

A one-at-a-time windows 63/252, targets 8%/12%, VIX20/30, bear 12/36 months and cap 1 use a common eligible window; zero-cost and separate 10/25 bps exposure charges and 1%/2% annual drags are labeled incomplete. Long-history A0/A1 begin after 126 observations without VIX and stay separate. B2/B3 test 6/9-month signals, top 2/top 4, skip month, 0/5/25/50 bps, each single exclusion, and one additional execution-session delay. B3 skip-month needs more warmup; before interpreting sensitivity performance the comparison is shifted to a shared 2007-10-31 execution start, preserving all data. Primary remains 2007-08-31.

For B3 the nine-month diagnostic is stronger than primary; it is not adopted. Skipping a month deepens drawdown to 24.73%, while removing GLD lowers CAGR to 5.28% on sensitivity dates. These show dependence on signal timing and gold diversification. At 50 bps costs sensitivity CAGR falls to 5.20%. The universe is correlated: four equity/real-estate tickers and two Treasury-duration tickers do not provide eight independent economic bets. Daily equity/duration exposure and concentration are exported. Worst strategy months are selected mechanically and retained.

| variant   | sample             |    CAGR |   Sharpe |   max_daily_drawdown |
|:----------|:-------------------|--------:|---------:|---------------------:|
| B0        | development        | 0.05474 |  0.42071 |             -0.37924 |
| B0        | validation         | 0.05089 |  0.61766 |             -0.15038 |
| B0        | historical_holdout | 0.08512 |  0.52719 |             -0.20677 |
| B1        | development        | 0.08833 |  0.60742 |             -0.25123 |
| B1        | validation         | 0.03892 |  0.35237 |             -0.21127 |
| B1        | historical_holdout | 0.12967 |  0.80375 |             -0.21568 |
| B2        | development        | 0.08267 |  0.58518 |             -0.25147 |
| B2        | validation         | 0.03716 |  0.33763 |             -0.19544 |
| B2        | historical_holdout | 0.11611 |  0.73954 |             -0.22642 |
| 60_40     | development        | 0.06364 |  0.61380 |             -0.32617 |
| 60_40     | validation         | 0.08819 |  1.22029 |             -0.10601 |
| 60_40     | historical_holdout | 0.09317 |  0.58757 |             -0.21298 |
| B3        | development        | 0.06196 |  0.66203 |             -0.14102 |
| B3        | validation         | 0.03780 |  0.34995 |             -0.17911 |
| B3        | historical_holdout | 0.10459 |  0.80501 |             -0.17317 |

| prototype   | left   | right   | sample             |   n_months |   block_months |   replications |   annual_excess_mean_difference |   annual_excess_mean_difference_low |   annual_excess_mean_difference_high |   Sharpe_difference |   Sharpe_difference_low |   Sharpe_difference_high |
|:------------|:-------|:--------|:-------------------|-----------:|---------------:|---------------:|--------------------------------:|------------------------------------:|-------------------------------------:|--------------------:|------------------------:|-------------------------:|
| A           | A1     | A0      | full               |        439 |              6 |           1000 |                         0.02939 |                             0.00336 |                              0.05669 |             0.35788 |                 0.15105 |                  0.54306 |
| A           | A1     | A0      | historical_holdout |         80 |              6 |           1000 |                         0.01480 |                            -0.03617 |                              0.07781 |             0.31980 |                 0.06667 |                  0.59285 |
| A           | A2     | A0      | full               |        439 |              6 |           1000 |                         0.01674 |                            -0.01262 |                              0.05331 |             0.30896 |                 0.08382 |                  0.57259 |
| A           | A2     | A0      | historical_holdout |         80 |              6 |           1000 |                         0.02458 |                            -0.01163 |                              0.07557 |             0.28497 |                 0.09579 |                  0.52804 |
| A           | A3     | A0      | full               |        439 |              6 |           1000 |                         0.02919 |                            -0.00579 |                              0.06698 |             0.50072 |                 0.20832 |                  0.76017 |
| A           | A3     | A0      | historical_holdout |         80 |              6 |           1000 |                         0.02044 |                            -0.04486 |                              0.10024 |             0.55144 |                 0.19626 |                  0.94588 |
| A           | A3     | A1      | full               |        439 |              6 |           1000 |                        -0.00019 |                            -0.01459 |                              0.01336 |             0.14283 |                 0.02588 |                  0.25997 |
| A           | A3     | A1      | historical_holdout |         80 |              6 |           1000 |                         0.00565 |                            -0.01121 |                              0.02551 |             0.23164 |                 0.02620 |                  0.45132 |
| B           | B1     | B0      | full               |        228 |              6 |           1000 |                         0.02297 |                            -0.02505 |                              0.06206 |             0.11957 |                -0.29291 |                  0.46115 |
| B           | B1     | B0      | historical_holdout |         80 |              6 |           1000 |                         0.04227 |                            -0.01923 |                              0.08814 |             0.27656 |                -0.29213 |                  0.63812 |
| B           | B2     | B1      | full               |        228 |              6 |           1000 |                        -0.00709 |                            -0.01882 |                              0.00186 |            -0.03660 |                -0.12796 |                  0.03814 |
| B           | B2     | B1      | historical_holdout |         80 |              6 |           1000 |                        -0.01303 |                            -0.04726 |                              0.00871 |            -0.06421 |                -0.37215 |                  0.12243 |
| B           | B3     | B2      | full               |        228 |              6 |           1000 |                        -0.01326 |                            -0.02510 |                              0.00411 |             0.04352 |                -0.06125 |                  0.16253 |
| B           | B3     | B2      | historical_holdout |         80 |              6 |           1000 |                        -0.01325 |                            -0.03263 |                              0.01267 |             0.06547 |                -0.09382 |                  0.22370 |
| B           | B2     | B0      | full               |        228 |              6 |           1000 |                         0.01588 |                            -0.03261 |                              0.05513 |             0.08297 |                -0.32096 |                  0.42679 |
| B           | B2     | B0      | historical_holdout |         80 |              6 |           1000 |                         0.02924 |                            -0.04224 |                              0.07730 |             0.21235 |                -0.42778 |                  0.60819 |
| B           | B2     | 60_40   | full               |        228 |              6 |           1000 |                         0.00104 |                            -0.04886 |                              0.03643 |            -0.14914 |                -0.61375 |                  0.19607 |
| B           | B2     | 60_40   | historical_holdout |         80 |              6 |           1000 |                         0.02166 |                            -0.05702 |                              0.10341 |             0.15197 |                -0.51316 |                  0.77918 |
| B           | B3     | 60_40   | full               |        228 |              6 |           1000 |                        -0.01222 |                            -0.05355 |                              0.02587 |            -0.10562 |                -0.59792 |                  0.27882 |
| B           | B3     | 60_40   | historical_holdout |         80 |              6 |           1000 |                         0.00841 |                            -0.06057 |                              0.08528 |             0.21744 |                -0.48726 |                  0.87398 |

## 7. Feasibility, costs and capital

B3 risky-asset turnover averages 3.14944 times capital annually (both sides counted);10 bps per traded dollar implies about 0.31% annual simple modeled cost allowance. Full-history sum of cost fractions is 0.05985, not a CAGR difference; gross reruns isolate compounded drag. Spread/slippage/commission allowance is assumed, not measured. ETF expenses embedded in prices are not deducted again; investor management fees, tax, whole-share rounding and operational cash-vehicle differences are excluded.

At each rebalance ADV20 is mean(Close*Volume) over 20 sessions through the previous signal close. Participation=initial_AUM*pretrade_NAV*abs(delta weight)/ADV20. Scenarios begin 1m/10m/50m and grow with B2/B3 net NAV, with no flows. Report p 95/max per ticker over rebalance opportunities (including zero-trade dates), and additionally nonzero-trade summaries. The table below is the evolving 10m B3 scenario; fractions are decimals. It is an all-day vendor-volume screen, not certified consolidated or auction liquidity.

DBC reaches 19.17% participation in the 10m scenario; therefore a universal single-close 10m mandate is not justified by this evidence. The 1m scenario scales participation one tenth, but remains provisional. Report 1% and 5% ADV illustrative maximum trade-size constraints by event; they are governance screens, not guaranteed safe capacity.50m magnifies these concerns. Current liquidity alone cannot justify historical capacity.

A practical mandate would require independent consolidated-volume and distribution checks, historical spreads/auction volume, stressed fill analysis, and an order deadline policy. Consider slicing orders across sessions only as a prospective rule to validate, because it changes current close-execution assumptions. ETF creation/redemption and underlying foreign-equity, Treasury or commodity liquidity affect spreads. GLD is a bullion trust; DBC is a futures commodity pool with roll/collateral/tax considerations; neither is a generic equity fund. Existing holdings are preserved if a feed/rebalance fails until data are verified and the issue escalated; no synthetic returns or silent substitution.

A's factor data cannot substantiate stock-level turnover, borrow availability, margin/funding access, or capacity. The conventional gross notional 2a can reach 3 per unit capital under cap 1.5. Illustrative exposure charges omit trading inside Mom and are not complete net evidence. A is suitable for course mechanism research, not an executable AUM pitch.

| variant   | ticker   |   initial_aum |   maximum |     p95 |   fraction_above_1pct |   fraction_above_5pct |
|:----------|:---------|--------------:|----------:|--------:|----------------------:|----------------------:|
| B3        | DBC      |      10000000 |   0.19174 | 0.03288 |               0.08734 |               0.03930 |
| B3        | EEM      |      10000000 |   0.00728 | 0.00258 |               0.00000 |               0.00000 |
| B3        | EFA      |      10000000 |   0.00984 | 0.00430 |               0.00000 |               0.00000 |
| B3        | GLD      |      10000000 |   0.00779 | 0.00324 |               0.00000 |               0.00000 |
| B3        | IEF      |      10000000 |   0.07717 | 0.02246 |               0.07860 |               0.01747 |
| B3        | SPY      |      10000000 |   0.00031 | 0.00019 |               0.00000 |               0.00000 |
| B3        | TLT      |      10000000 |   0.01046 | 0.00530 |               0.00873 |               0.00000 |
| B3        | VNQ      |      10000000 |   0.03111 | 0.01923 |               0.09170 |               0.00000 |

## 8. Recommendation and limitations

Recommend a research-stage B3 pitch for investors who value explicit risk limits and accept lower participation in gains. The executable ETF holdings, monthly audit trail and no-leverage cap fit the assets objective better than a synthetic factor. B1 should remain a serious comparator because it produces higher historical return; B2's simpler filter offers little improvement in the worst drawdown here. B3's downside reduction is useful but largely consistent with lower exposure, and full-sample 60/40 Sharpe is higher. No reliable superiority claim survives uncertainty and all practical assumptions.

The initial 10m proposal remains illustrative, contingent on execution validation. The next milestone is independent data and auction/impact checks on a 1m scenario, then prospective paper decisions recorded before realized returns, without tuning the primary rule from the inspected holdout. Do not allocate live capital based on this homework. This is the specification's honest research-stage outcome when evidence is mixed.

Principal risks: trend reversals and fast rebounds, range-bound whipsaw, persistent regime change, simultaneous stock/bond weakness, correlated equity/duration concentration, gold dependence, cash opportunity cost and vehicle/credit/reinvestment risk, provider revisions/outages, tax and fee exclusions, and historical universe choice. A cap estimates historical risk and is not a maximum loss guarantee. A fully independent data source, richer execution estimates, longer genuine prospective evidence or sustained net advantage could change the conclusion. Material unexplained data differences, failed NAV/timing checks, repeat operational failures or liquidity breaches would suspend new rebalances and trigger review. Do not retrofit a shutdown rule into the historical backtest.

## 9. Investor questions and answers

Why might momentum persist? Delayed information incorporation, behavioral feedback and risk compensation are plausible published explanations; none guarantees our portfolio's premium.

What is new? Transparent controlled comparisons and an auditable implementation; relative/absolute momentum and volatility caps are established. No discovery of sector-neutral stock selection or new alpha.

How does it differ from buy-and-hold, stock momentum ETFs and CTAs? We rotate long-only cross-asset ETF slots, compare each selected slot to cash and optionally cap risk. Stock momentum ETFs select within equities; futures CTAs can short declines and engineer rolls/collateral. We do neither.

Is reduced drawdown just less risk? Much of B3's protection is accompanied by 22.82% average cash and lower volatility/return. A1's full-history mean unit exposure is close to 1, but its timing changes which periods carry risk. No free alpha claim.

When does it fail? Fast reversals, noisy range-bound markets and concentrated long exposures can lose or miss rebounds. In 2020 B3 lagged SPY/60-40 despite less downside; in 2022 it still lost money.

How were tickers/parameters selected and how many variants tried? They were specified before this execution, fixed before downloads/performance, with the complete ledger exported. Today's eight ETFs create retrospective selection bias; no alternative winner was promoted.

Is holdout future evidence? No:2020 onward is publicly known historical validation and was inspected for comparisons. Prospective time-stamped paper trading is the next test.

What is excluded? Measured spreads/impact, funding/borrow for A, investor fees/taxes, precise auction fills, cash implementation and vendor revisions. ETF expenses remain embedded.

How much capital?1m/10m/50m are modeled scenarios. Historical all-day vendor ADV flags show 10m is not universally compatible with small participation; no certified safe capacity. Need auction and underlying-market evidence.

What invalidates the thesis? A persistent failure of net return/risk tradeoffs in prospective frozen-rule evidence, unexplained data/accounting defects, repeated execution problems or capacity breaches warrants formal review and suspension of new decisions.

What follows a missing feed or failed rebalance? Preserve existing holdings pending verified data, escalate and log the missed decision; never invent data or silently change the rule.

## 10. Reproduction and references

README.md contains commands: install pinned requirements, validate cached inputs, pytest, run --offline, report --offline, execute notebooks, and compare clean-run hashes. Python source modules implement one shared backtest; notebooks explain and call them. Data/return/holdings tables retain full precision; report decimal metrics show five digits. Tests and cached reproduction evidence are in outputs/audits, with an acceptance checklist in research.

Uploaded sources: Achilles Venetoulias, B9339 Lectures 3-5 Momentum, Fall 2026, slides 4-7, 17-23, 42-49, 65-88; Homework 2 handout. Daniel & Moskowitz (2016), Momentum crashes, Journal of Financial Economics 122, 221-247. Asness, Frazzini, Israel & Moskowitz (2014), Fact, Fiction and Momentum Investing, Journal of Portfolio Management. Kolanovic & Wei (2015), Momentum Strategies Across Asset Classes: Risk Factor Approach to Trend Following, pp 19-20, 59-60. Baltas & Kosowski (supplied January 5, 2013 version), Momentum Strategies in Futures Markets and Trend-Following Funds, section 3. Exact local excerpt locations and issuer URLs: research/source_map.md.

Provider methodology: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor_daily.html ; https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor.html ; https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/changes_crsp.html ; https://www.cboe.com/tradable_products/vix/vix_historical_data ; https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html . Accessed October 4, 2026. Input URLs and acquisition vintages are in manifests/inputs.json. Yahoo data are personal academic caches, not a public redistribution authorization.

