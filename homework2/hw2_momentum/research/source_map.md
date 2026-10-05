# Source map

Accessed October 4, 2026. Published findings below are motivation, never substituted for our measured results. Local line locations refer to supplied markdown; PDF page numbers are included where recoverable.

| Claim / formula | Resolved supplied file and location | Outside source / application |
|---|---|---|
| Investor objective, landscape, technical detail, innovation, robustness, feasibility and Q&A | ../homework/hw2/hw2.md, lines 1-88 | Requirements matrix; user explicitly resolves deadline to Eastern |
| Absolute=time-series; relative=cross-sectional; twelve-month dual signal includes latest month and compares cash hurdle | ../2 momentum.md, slides 4-7,22-23,42-44; lines 29-106,260-450 | B uses eight ETFs and three slots, not exact four-module lecture replication |
| Stock momentum skip-month and ranking volatility adjustment distinct from exposure management | ../2 momentum.md, slide 18, lines 208-220 | A cannot reconstruct stock rankings or sector neutrality |
| Panic state, past market weakness, high ex-ante volatility, loser rebound asymmetry | ../readings/momentum/Momentum crashes.md, abstract/introduction pp221-223 lines 1-170; section3 pp226-227 lines390-440 | A bear+VIX heuristic motivated by mechanism; not replication |
| Conditional expected mean/variance dynamic weighting differs from inverse-volatility sizing | Same, section4 p233 lines1238-1295 | Scrambled equation (6) not implemented; only qualitative distinction used. No GARCH or fitted means |
| Widespread momentum evidence; theory uncertain; turnover costs and value diversification matter | ../readings/momentum/Fact, Fiction and Momentum Investing.md, pp2-4 lines20-145, Myth5, Myth8, Myth9-10 pp18-22 | Our eight-ETF portfolio does not inherit published Sharpe, capacity, or tax findings |
| Relative ranks versus absolute individual signals; one-day signal gap; 10bps assumption; EMV | ../readings/momentum/Momentum Strategies Across Asset Classes Risk Factor Approach to Trend Following.md, pp19-20 lines620-725 | B equal slots differs from EMV and futures shorting |
| Tuning risks; portfolio vol targeting not always useful; VIX heuristic | Same, pp59-60 lines2835-2918 | A shares threshold25 but uses combined bear/VIX states; B vol cap may reduce returns |
| TSM direction and inverse volatility; monthly/weekly/daily differences; capacity not universally proven | ../readings/momentum/Momentum Strategies in Futures Markets and Trend-Following Funds.md, abstract/introduction pp1-4 lines1-150; section3 pp8-9 lines291-350 | Published futures capacity results not transferable to ETFs; our B uses long/cash |
| French Mom six size/prior-return portfolios, high minus low, daily formed daily | none (provider methodology) | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor_daily.html |
| Monthly Mom formed monthly | none | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor.html |
| FIZ/CIZ changes and historical revisions | none | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/changes_crsp.html ; https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html |
| VIX closes, official historical series | none | https://www.cboe.com/tradable_products/vix/vix_historical_data ; actual CSV URL in inputs.json |
| Yahoo adapter settings, exclusive end date | installed yfinance1.7.0 signatures in manifests/yfinance_api.txt | https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html |

## ETF issuer checks

| Ticker | Issuer / structure | Inception or launch | Issuer source |
|---|---|---|---|
| SPY | State Street, S&P500 unit investment trust | 1993-01-22 | https://www.ssga.com/us/en/institutional/etfs/state-street-spdr-sp-500-etf-trust-spy |
| EFA | BlackRock/iShares, developed ex-US equity ETF | 2001-08-14 | https://www.ishares.com/us/products/239623/ishares-msci-eafe-etf |
| EEM | BlackRock/iShares, emerging equity ETF | 2003-04-07 | https://www.ishares.com/us/products/239637/ishares-msci-emerging-markets-etf |
| IEF | BlackRock/iShares, 7-10yr Treasury ETF | 2002-07-22 | https://www.ishares.com/us/products/239456/ishares-710-year-treasury-bond-etf |
| TLT | BlackRock/iShares, 20+yr Treasury ETF | 2002-07-22 | https://www.ishares.com/us/products/239454/ishares-20-year-treasury-bond-etf |
| GLD | SPDR Gold Trust, physical bullion trust | trading 2004-11-18 | https://www.spdrgoldshares.com/usa/gld/ |
| DBC | Invesco DB, commodity futures pool with collateral | 2006-02-03 | https://www.invesco.com/us/en/financial-products/etfs/invesco-db-commodity-index-tracking-fund.html ; issuer Q1 2026 factsheet |
| VNQ | Vanguard, listed real estate equity ETF | 2004-09-23 | https://advisors.vanguard.com/investments/products/vnq/vanguard-real-estate-etf |

All eight have active issuer product pages and observations through cutoff. Actual Yahoo history often begins after legal inception; eligibility follows observed history, never backfilled issuer inception. DBC earliest observed date 2006-02-06 binds the common universe. GLD trust formation date differs from first trading date. US-listed USD sessions do not remove foreign equity/currency risks or underlying-market timing differences.

Targeted issuer cash distributions and a June2026 month-end return were compared late in QA, plus an independent Nasdaq/PHLX split notice. Precision/definition differences are retained in independent_provider_checks.csv and corporate_actions.md. Full independent adjusted-price history and volume certification remain incomplete. No Databento access queried or costs incurred; no WRDS work.

Provider field convention and targeted corporate actions: https://help.yahoo.com/kb/SLN28256.html ; https://www.ishares.com/us/products/239637/ishares-msci-emerging-markets-etf (distribution table; June30,2026 performance table); https://classic.nasdaqtrader.com/content/phlxmemos/2008/Jul/1410-08.pdf (memo1410-08). Access October4,2026.
