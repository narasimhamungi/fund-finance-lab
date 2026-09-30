# fund-finance-lab

![CI](https://github.com/narasimhamungi/fund-finance-lab/actions/workflows/ci.yml/badge.svg)

Stress models for the two main fund-finance facilities: **NAV loans**, secured on a fund's portfolio, and
**subscription lines**, secured on investors' uncalled commitments. Each model shows how the lender's protections
(LTV covenants, cash sweeps, borrowing-base eligibility) behave when the portfolio falls or investors drop out.

> Inputs in `examples/` are **hypothetical and illustrative**, except `cef_coverage_csq_fy2021.json`, which is taken
> from a public filing (source inside the file). They are not observed market terms, not advice,
> and not any rating agency's methodology.

## Status

- [x] NAV facility: eligible NAV after a single-asset cap and an optional top-N limit, LTV, a diversity covenant,
      uniform drawdown to the sweep and breach levels, cure amount, largest-asset loss scenarios
- [x] Subscription line: borrowing base by investor category, availability, mandatory prepayment, uncalled-capital
      coverage, exclusion and default scenarios
- [x] Unit tests and CI
- [x] Explainer: subscription lines vs NAV loans (collateral, advance rates, covenants), with sources: [`docs/explainer.md`](docs/explainer.md)
- [x] Excel workbook reproducing the NAV model in formulas, with an input sheet, consistency checks and a
      cross-check against the Python results on the shipped inputs: [`excel/nav_facility_stress.xlsx`](excel/nav_facility_stress.xlsx)
- [x] Regression suite for the workbook: 48 cases (shipped configs, 10 edge cases, 36 seeded random cases) with
      Python-expected outputs; LibreOffice 24.2 evaluates the workbook on every case and passes 912 of 912 checks
      ([`excel/regression/`](excel/regression/)). Its first run found a defect in the workbook's breakeven check
      (failed for every portfolio already in breach, `#DIV/0!` at zero loan), now fixed
- [ ] VBA harness running the same cases inside Excel: specified with acceptance tests in
      [`docs/vba_regression_harness.md`](docs/vba_regression_harness.md), not built
- [x] Closed-end fund asset coverage: section 18 calculator (reproduces a real fund's reported coverage) and a
      legal-document memo on the tests, preferred-share covenants and remedies: [`docs/cef_coverage_memo.md`](docs/cef_coverage_memo.md)

## Run

```bash
pip install -e ".[test]"
pytest -q
fund-finance-lab nav --config examples/nav_facility_hypothetical.json --out outputs/nav
fund-finance-lab subline --config examples/subscription_line_hypothetical.json --out outputs/subline
fund-finance-lab nav --config examples/nav_facility_covenants_hypothetical.json --out outputs/nav_covenants
fund-finance-lab coverage --config examples/cef_coverage_csq_fy2021.json --out outputs/coverage_csq_fy2021
python excel/build_nav_workbook.py   # optional: rebuild the workbook (needs openpyxl)
fund-finance-lab regression-cases    # rebuild excel/regression/cases.csv after any model change
python excel/regression/run_libreoffice.py   # optional: evaluate the workbook on every case (needs LibreOffice)
fund-finance-lab verify-log --log excel/regression/libreoffice_log.csv
```

Each run writes CSVs and a summary (`nav_summary.md`, `subline_summary.md`). To model a different facility, copy an
example file and change the inputs; the units are whatever you enter.

## Layout

| Path | Purpose |
|---|---|
| `src/fundfinancelab/nav_facility.py` | NAV facility: eligibility, LTV, breakeven drawdowns, cure, single-name stress |
| `src/fundfinancelab/subscription_line.py` | Subscription line: borrowing base, availability, coverage, investor scenarios |
| `src/fundfinancelab/asset_coverage.py` | Closed-end fund asset coverage (section 18): ratios, headroom, cure, distribution capacity |
| `src/fundfinancelab/regression.py` | Workbook regression cases with Python-expected outputs, and the log verifier |
| `src/fundfinancelab/cli.py` | Command line and summaries |
| `examples/` | Hypothetical inputs, including a facility with concentration and diversity covenants |
| `excel/` | The NAV model as a formula-driven workbook, and the script that builds it |
| `excel/regression/` | Regression cases, the LibreOffice runner and its log |
| `docs/vba_regression_harness.md` | Contract and acceptance tests for the Excel (VBA) run of the regression cases |
| `docs/explainer.md` | Subscription lines vs NAV loans: collateral, sizing, covenants, how agencies look at them, and where these models are simpler |
| `docs/model_spec.md` | Every formula the models use |
| `docs/cef_coverage_memo.md` | Legal-document review: a leveraged closed-end fund's coverage tests and remedies |
| `docs/limitations.md` | What the models leave out |
