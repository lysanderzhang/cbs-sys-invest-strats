"""Generate the prioritized audit, assignment checklist and verification handoff."""
from pathlib import Path
import json,re,hashlib
import pandas as pd
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]

def main():
    audit=ROOT/'results/audit';v=json.loads((audit/'verification.json').read_text());pages=len(PdfReader(ROOT/'report/main.pdf').pages)
    rows=[
      ('(a)','12 tenor/size/allocation combinations; nine non-USD currencies','PASS','Report Section 2; representative_holdings.csv; baseline_returns.csv'),
      ('(a)','Explicit dated currencies/weights for every construction','PASS','12-row holdings table; daily_weights.csv, all 321,840 positions'),
      ('(a)','Daily ranks, normalized long/short weights and next-period application','PASS','Independent full-path weights/rank checks and timing tests'),
      ('(b)','Arithmetic/geometric returns, volatility, Sharpe, skew/kurtosis, VaR/ES, drawdown and wealth','PASS','Section 3; baseline_performance.csv, wealth/drawdown/distribution figures'),
      ('(b)','Paired tenor, number-per-side and allocation comparisons; consistent winner','PASS','Paired design effects; 3M_3_equal selected by Sharpe'),
      ('(b)','2008 stress comparison','PASS','All 12 in baseline_2008.csv; crisis discussion and supporting figure'),
      ('(c)','All six indicators, contemporaneous changes and predictive level regimes','PASS','Section 4; correlations, regime moments/counts/probabilities'),
      ('(c)','Economic relevance, candidate choice and direct Jurek answer','PASS WITH LIMITS','AY3M/AY1wk essentially tied; qualitative stress support, not crash-premium replication'),
      ('(d)','Six common-rule conditioned strategies with prior-only thresholds','PASS','Section 5; all six full/common returns, exposures and thresholds independently checked'),
      ('(d)','Common sample, active exposure, consistent selection and trade-offs','PASS','2727 shared dates; AY3M point-estimate winner; exposure controls and missed gains'),
      ('(d)','Look-ahead and robustness of volatility timing','PASS WITH LIMITS','No computational look-ahead; unknown fixings; extra selection/exposure lag changes winner to AY6M'),
      ('(e)','Historical volatility construction, units and same conditioning rule','PASS','Section 6; AUDJPY=raw AUD*raw JPY; 21 arithmetic returns, ddof=1, sqrt(252)'),
      ('(e)','Realized/implied/baseline comparison on common dates and interpretation','PASS WITH LIMITS','2707 dates; complete moments/tails; AY3M-vs-historical Sharpe interval includes zero'),
      ('General','Arithmetic daily returns, interest accrual and zero transaction costs','PASS','Exact USD deposit/borrowing formula and exact spot/carry/interaction decomposition'),
      ('General','First-page answers, five-decimal precision, formulas and references','PASS',f'{pages}-page report; first page (a)-(e); Jurek (2014) and Barclays Capital (2011)'),
      ('General','Reproducibility and data preservation','PASS','Shared course interpreter; dependency specification; original input hashes verified'),
    ]
    pd.DataFrame(rows,columns=['question','requirement','status','evidence']).to_csv(audit/'compliance.csv',index=False)
    controls=pd.read_csv(audit/'exposure_controls.csv',index_col=0);lag=pd.read_csv(audit/'additional_decision_lag.csv',index_col=0)
    ci=pd.read_csv(audit/'filter_sharpe_intervals.csv',index_col=0);cie=pd.read_csv(audit/'historical_sharpe_intervals.csv',index_col=0)
    c=controls.loc['AY3M'];a=ci.loc['AY3M'];h=cie.loc['AY3M minus historical']
    testlog=(ROOT/'results/validation/pytest.txt').read_text();tests=int(re.search(r'(\d+) passed',testlog).group(1))
    old=json.loads((audit/'prior_numerical_hashes.json').read_text())
    changes=[name for name,digest in old.items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest]
    inputs=[]
    for row in json.loads((ROOT/'data/manifest.json').read_text()):
        assert hashlib.sha256((ROOT/row['copy']).read_bytes()).hexdigest()==row['sha256'];inputs.append(row['copy'])
    pages=len(PdfReader(ROOT/'report/main.pdf').pages)
    lines=['# HW3 review: corrections, completeness and verification','',
      'The review reconstructed the supplied sample from the original CSV without importing the production financial functions. No error was found in the observed-sample currency-return formula, interest accrual, portfolio construction, rebalancing lag, or primary performance calculations. The corrections concern demonstrated validation defects and materially incomplete interpretation/robustness evidence.','',
      '## A. Prioritized errors and corrections','',
      '1. **High — invalid inputs could pass validation.** The old finite-value check omitted yields and dropped entire rows with missing VIX. Infinite AUD yields, and an infinite AUD spot on the initial missing-VIX row, were accepted in two explicit probes. Corrected validation checks every observed numeric input, retains permitted missing volatility, and rejects invalid compounding paths. Regression tests cover both probes. The actual supplied data contain neither defect, so primary results do not change.','',
      '2. **High — the old report check could approve a wrong metric.** It accepted a number if the same value appeared anywhere in any table, and hard-coded a 19-page document. Replaced with source-file/row/column/unit-specific numerical bindings, stale-file hashes, and a dynamic page count. Tests now reject a baseline Sharpe replaced by an existing conditioned Sharpe, or incorrect metric/units. No such mismatch remains in the final report.','',
      f'3. **High — the exact winning filter is timing-sensitive.** The prior robustness check delayed weights only. A new check delays both currency selection and the exposure decision, on identical dates. AY3M Sharpe is {lag.loc["AY3M_lagged","sharpe"]:.5f}, while AY6M reaches {lag.loc["AY6M_lagged","sharpe"]:.5f} and becomes the winner. The primary AY3M result remains correct, but a unique robust winning signal is not established.','',
      f'4. **Medium — reduced exposure had not been isolated.** On the original common sample, AY3M drawdown is {100*c.filtered_drawdown:.5f}% versus {100*c.constant_drawdown:.5f}% for uniform exposure equal to its active fraction, and {100*c.volmatched_drawdown:.5f}% for a volatility-matched baseline. The sample benefit is more than uniform deleveraging; both controls use ex-post scaling and are diagnostics, not causal or live-strategy estimates. All six controls, active-day ES and skipped gains/losses are exported.','',
      f'5. **Medium — point-estimate rankings lacked uncertainty evidence.** Paired 20-observation moving-block bootstrap intervals use 2,000 replications and seed 9339, without parameter tuning. AY3M-minus-baseline Sharpe has pointwise interval [{a.ci_low:.5f}, {a.ci_high:.5f}]. AY3M-minus-historical has [{h.ci_low:.5f}, {h.ci_high:.5f}], including zero. Intervals condition on the selected realized series and do not adjust for choosing the best baseline/filter; no out-of-sample significance claim is made.','',
      '6. **Medium — narrative precision and presentation.** The final '+str(pages)+'-page report includes the main analysis and integrated figure appendix, retains complete answers and key formulas, and removes operational discussion. All critical narrative numerical results have explicit source bindings. The AY3M/AY1wk predictive ES contrast is described as effectively tied, not precise evidence of signal superiority.','',
      '7. **Low — CSV/XLSX precision needed a ranking check.** Higher workbook precision changes spread weights slightly but changes no selected currency set or equal/rank weights. Both source versions select 3M_3_equal and AY3M. The primary CSV convention is retained and disclosed; source_precision.csv and source_precision_filters.csv report the full comparison.','',
      '## B. Requirement-by-requirement checklist','',
      '| Question | Requirement | Outcome | Evidence |','|---|---|---|---|']
    for question,requirement,status,evidence in rows:lines.append('| '+' | '.join([question,requirement,status,evidence])+' |')
    lines.extend(['','## C. Corrections to code and numerical outputs','',
      '- `src/data.py`: complete numeric/schema validation, including yields and rows with missing volatility.',
      '- `src/performance.py`: reject nonfinite returns and returns at/below -100% rather than silently calculating invalid wealth.',
      '- `src/run.py`: check plotted line data against directly compounded returns and drawdowns.',
      '- `src/review.py`: separate complete reconstruction and exposure/lag/bootstrap diagnostics.',
      '- `src/review_sources.py`: independent cross-file precision check.',
      '- `src/report.py` and `src/validate_report.py`: source-bound claims, shorter report and stale-audit detection.',
      '- `src/package.py`: dynamic verification/page counts and current-PDF visual-review requirement.','',
      f'Primary numerical files compared with the pre-review snapshot: {len(old)}; changed files: {changes or "none"}. Corrected defensive code does not alter the supplied-sample outcomes. New diagnostic tables are additional evidence, not reoptimized strategies.','',
      '## D. Verification summary','',
      f'- {v["checks"]} independent checks across {v["values_checked"]:,} numeric values passed.',
      f'- {tests} tests passed using the existing shared FINCB9339 interpreter.',
      '- Every daily currency rank/weight and exact currency/portfolio return is reconstructed; USD term cancellation and spot/carry/interaction contributions reconcile.',
      '- All six raw/as-of/threshold/exposure/return paths, both regime timings and every conditional statistic are checked.',
      '- AUDJPY cross, each 21-day realized standard deviation, historical thresholds/exposures, and common evaluation windows are independently checked.',
      '- Arithmetic/geometric annualization, sample volatility, adjusted skew/kurtosis, empirical VaR/ES, terminal wealth and initial-wealth drawdown are recalculated.',
      '- Future-suffix perturbation and an integrated production return/filter mutation test find no computational look-ahead.',
      '- Five representative dates cover 60 dated portfolio reconstructions, including September 15 and October 24, 2008; manual_observations.csv gives decomposition and calendar accrual days.',
      '- Figure line data are checked at the plotting boundary; final figures are generated from reconciled series. PDF pages are visually reviewed before packaging.',
      '- All five input-copy hashes match the original manifest; no data source was edited or silently repaired.','',
      '## E. Unresolved limitations','',
      '1. Within-day fixing timestamps are not supplied. A closing-row lag establishes computational chronology, not availability at an executable common fixing. The extra-lag winner change is material.',
      '2. Annual percentage term yields are modeled as continuous daily financing proxies on ACT/365; the original deposit compounding convention and true overnight funding are not established. ACT/360 is only a sensitivity.',
      '3. AY1wk contains long constant runs; VIX gaps are carried forward. Quote freshness and holiday conventions cannot be independently certified from these inputs.',
      '4. All baseline/signal selection is in sample. Block intervals are pointwise conditional descriptions, not a multiple-selection-adjusted or prospective investment test.',
      '5. Zero trading costs are required by the assignment. Daily-turnover capacity, implementation frictions and option-insurance costs are outside this backtest.',
      '6. VIX is not Jurek\'s equity downside factor, and volatility filtering does not replicate crash-neutral option hedging or identify a variance/crash risk premium.',''])
    (ROOT/'report/AUDIT.md').write_text('\n'.join(lines))
    summary=dict(independent_checks=v['checks'],independent_values=v['values_checked'],tests_passed=tests,
        primary_numerical_files_compared=len(old),primary_numerical_files_changed=changes,input_hashes_verified=inputs,report_pages=pages,
        no_computational_lookahead_found=True,actual_fixing_availability_verified=False,uncertainty_selection_adjusted=False)
    (audit/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

if __name__=='__main__':main()
