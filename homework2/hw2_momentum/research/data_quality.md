# Data quality and coverage

| dataset    | start               | end                 |   rows |   missing |   duplicates |
|:-----------|:--------------------|:--------------------|-------:|----------:|-------------:|
| factor     | 1926-11-03 00:00:00 | 2026-08-31 00:00:00 |  26216 |         0 |            0 |
| etf_prices | 2006-02-06 00:00:00 | 2026-08-31 00:00:00 |   5174 |         0 |            0 |
| SPY        | 1993-01-29 00:00:00 | 2026-09-30 00:00:00 |   8475 |         0 |            0 |
| EFA        | 2001-08-27 00:00:00 | 2026-09-30 00:00:00 |   6310 |         0 |            0 |
| EEM        | 2003-04-14 00:00:00 | 2026-09-30 00:00:00 |   5904 |         0 |            0 |
| IEF        | 2002-07-30 00:00:00 | 2026-09-30 00:00:00 |   6082 |         0 |            0 |
| TLT        | 2002-07-30 00:00:00 | 2026-09-30 00:00:00 |   6082 |         0 |            0 |
| GLD        | 2004-11-18 00:00:00 | 2026-09-30 00:00:00 |   5500 |         0 |            0 |
| DBC        | 2006-02-06 00:00:00 | 2026-09-30 00:00:00 |   5195 |         0 |            0 |
| VNQ        | 2004-09-29 00:00:00 | 2026-09-30 00:00:00 |   5536 |         0 |            0 |

No duplicate dates. No missing ETF observations on the common factor-session calendar 2006-02-06 to 2026-08-31. No missing French daily inputs. VIX backward join only; max accepted staleness 1 calendar days. Pre-1990 VIX remains missing, never extended. 2 >20% daily ETF moves flagged and retained for review.

Yahoo Adj Close includes distributions: no cash dividend is added again. Corporate-action checks compare adjusted returns with (close + distribution)/previous close, including every supplied split event and first/last distributions. Differences reflect Yahoo backward adjustment/reinvestment convention and precision; these are internal return reconciliations. EFA2005 and EEM2005/2008 split events are preserved. Provider Close is historical split-adjusted, distinct from dividend-adjusted Adj Close; it must not be called original pre-split transaction price. Capacity uses provider Close*Volume as a vendor dollar-volume proxy. Historical volume split normalization, consolidated venue scope and closing-auction volume are not independently certified; safe capacity is therefore provisional. Targeted issuer/venue event checks are documented separately in research/corporate_actions.md; a complete independent adjusted-price/month-end return reconciliation remains unavailable. All cached input files are for authorized personal academic use; no publication/redistribution license is inferred. Databento was unnecessary and unused.

French files are CIZ-era snapshots; current historical values may be revised. Daily size/momentum portfolios are formed daily; monthly Mom portfolios are formed monthly. RF and market data differ in aggregation conventions across frequencies; official monthly series are not used to substitute daily cash. Primary endpoints follow French daily RF/Mom August 31, 2026; September ETF/VIX observations are unused.
