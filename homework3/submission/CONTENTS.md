# HW3 final reviewed submission

- `final_report.pdf`: 20-page complete report with an integrated nine-figure appendix; all answers (a)-(e) on the first page and all 13 graphs included once. Submit this single PDF as the write-up.
- `final_report.tex` and `references.bib`: local, Git-ignored submission source copies; canonical sources are under `report/`. `FIGURE_GUIDE.md` identifies appendix figures.
- `AUDIT.md`: prioritized corrections, full requirement checklist, verification and unresolved limitations.
- `verification_summary.json` and `compliance.csv`: compact verification record and requirement checklist.
- `research_project.zip`: complete project rooted at `homework3/`, including source, raw inputs, references, LaTeX, daily weights/returns, all six filters, historical filter, tables, figures and tests.
- `research_manifest.json`: SHA-256 digests of the 148 archived research files.

Verification: 30 passing tests; 144 independent checks across 958,020 values. All original primary numerical exports remain unchanged. The exact winning filter changes under an additional decision lag; implied-versus-historical superiority is not established statistically. See the audit for full qualifications.

To reproduce, extract the ZIP, enter `homework3/`, and follow README.md using the existing shared course environment. No project-local environment, dependency synchronization or external submission is performed. Caches, compiler executables, earlier drafts and temporary previews are excluded.

Report SHA-256: `98b137cc0813d6ce7c1e9164a276aae2826d13bbfc161f5193da79632539ffae`

Archive SHA-256: `878b86ff84ed93b8dc63af19dd585e0155b29a9880207eb6e8ed714f754fdef3`
