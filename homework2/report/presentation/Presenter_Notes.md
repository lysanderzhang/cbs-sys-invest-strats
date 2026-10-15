# Presenter notes: Cross-Asset Dual Momentum with a Volatility Cap

Hanyu Zhang, Columbia University. October 5, 2026.

Slides 1–12 are the pitch (about 10–12 minutes). Slides 13–21 are backup.

## Main deck

1. **Executive summary.** Open with the problem we solve: static portfolios lose a third of their value in crises. B3's worst drawdown was −17.9%, against −32.6% for 60/40 and −55.2% for SPY. In 2022, when stocks and bonds fell together, B3 lost 5.0%; 60/40 lost 16.7%. It earns the most return per unit of drawdown of anything we tested. The ask: a $1m launch mandate, scaling to $10m after independent data and execution checks.
2. **Landscape.** Momentum is one of the most widely documented return patterns. The best-known forms need shorting, futures or leverage. Our niche is the same evidence in a long-only, unlevered, liquid-ETF form with a risk cap an allocator can monitor.
3. **Research foundation.** Our factor research shows momentum's worst losses cluster in high-volatility states: risk controls cut the factor's drawdown from −63% to −19%. B3 applies that principle in an investable form. The factor study is synthetic and gross, so we don't compare its returns with B.
4. **Data and timing.** Public, documented sources. Signals are computed a full session before trading, so there is no look-ahead. Every ETF strategy and benchmark starts on the same date, 2007-08-31.
5. **Construction.** Rank on 12-month return, take the top three, then test each against cash. A failed slot stays in cash, which is what makes the filter a real risk reduction.
6. **Risk control.** When B2's recent volatility exceeds 10%, exposure scales down proportionally. The cap never adds leverage. Walk through the example: 16% volatility gives q = 0.625 and 58% cash.
7. **Results.** Each step adds something: relative selection raises return and cuts drawdown; the volatility cap delivers the largest drawdown reduction. Versus 60/40, B3 gives up 1.3 points of return for a 45% shallower worst drawdown. Be upfront that 60/40 has the higher Sharpe; B3 is for investors who prioritize drawdown.
8. **Paths.** B3 compounds steadily and stays out of the deep troughs (2008–09, 2022). Log wealth scale; same dates and costs for all.
9. **Consistency.** B3 had much smaller drawdowns in 2007–2013 (−14.1% vs −32.6%) and led 60/40 on return and Sharpe in 2020–2026. In calm 2014–2019 markets, 60/40 did better, which is when we expect B3 to lag. We reviewed 2020–2026 during research, so we call it supporting evidence. The bootstrap shows the Sharpe gap to 60/40 is not significant either way; our case is drawdown.
10. **Robustness.** Drawdown stays within −14% to −25% across every variant. Execution delay is harmless; 50 bps costs still leave 5.2% CAGR. Gold matters, and we disclose that. We kept the pre-specified 12-month rule even though 9 months tested better, which is evidence of discipline.
11. **Implementation.** One rebalance a month, about 0.31% a year in modeled costs. At $1m every trade stayed under 2% of daily volume. DBC is the only meaningful capacity constraint at $10m, which is why we stage the mandate.
12. **Proposal.** Three reasons to allocate: drawdown control, protection when stocks and bonds fall together, and full transparency. Name the risks with their mitigants, then close on the ask and next steps.

## Appendix (backup)

13. Contents.
14. Factor overlay construction: bear and VIX flags, volatility scale capped at 1.5 factor units.
15. Factor results: synthetic gross; March–May 2009 shows the controls stepping aside from the crash.
16. Factor wealth and drawdown.
17. Accounting and metric definitions, with a drift example.
18. B3 exposure over time: average 77% invested; exposure drops in turbulent periods.
19. Five-decimal results table.
20. References.
21. Data provenance and reproducibility.

## Likely questions

**Why not just own 60/40?** 60/40 earned 1.3 points more a year with a higher Sharpe, but it fell 32.6% at its worst and 16.7% in 2022. B3 is for investors who cannot or will not sit through those losses.

**Isn't this just holding more cash?** Lower exposure in turbulent periods is the mechanism, by design. The value is that the rule decides when to de-risk, systematically and in advance.

**Why keep the cash filter if the cap does the work?** It is part of the pre-specified design, and changing it after seeing results would be overfitting.

**Can it take $10m today?** Not without checks. At $1m every trade is under 2% of daily volume; DBC needs order sizing at $10m, which is why the mandate is staged.

**Why not offer the factor strategy, which looks stronger?** It is a synthetic, gross factor study without stock-level trading, financing or borrow costs. It informs the design but is not an investable product.
