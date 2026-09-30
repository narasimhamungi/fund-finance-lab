# fund-finance-lab

![CI](https://github.com/narasimhamungi/fund-finance-lab/actions/workflows/ci.yml/badge.svg)

Stress models for the two main fund-finance facilities: **NAV loans**, secured on a fund's portfolio, and
**subscription lines**, secured on investors' uncalled commitments. Each model shows how the lender's protections
(LTV covenants, cash sweeps, borrowing-base eligibility) behave when the portfolio falls or investors drop out.

> All inputs in `examples/` are **hypothetical and illustrative**. They are not observed market terms, not advice,
> and not any rating agency's methodology.

## Status

- [x] NAV facility: eligible NAV after a single-asset cap and an optional top-N limit, LTV, a diversity covenant,
      uniform drawdown to the sweep and breach levels, cure amount, largest-asset loss scenarios
- [x] Subscription line: borrowing base by investor category, availability, mandatory prepayment, uncalled-capital
      coverage, exclusion and default scenarios
- [x] Unit tests and CI
- [x] Explainer: subscription lines vs NAV loans (collateral, advance rates, covenants), with sources: [`docs/explainer.md`](docs/explainer.md)
- [x] Excel workbook reproducing the NAV model in formulas, with an input sheet, consistency checks and a
      cross-check against the Python results: [`excel/nav_facility_stress.xlsx`](excel/nav_facility_stress.xlsx)
- [ ] Legal-document memo: leveraged closed-end fund asset-coverage tests (pending)

## Run

```bash
pip install -e ".[test]"
pytest -q
fund-finance-lab nav --config examples/nav_facility_hypothetical.json --out outputs/nav
fund-finance-lab subline --config examples/subscription_line_hypothetical.json --out outputs/subline
fund-finance-lab nav --config examples/nav_facility_covenants_hypothetical.json --out outputs/nav_covenants
python excel/build_nav_workbook.py   # optional: rebuild the workbook (needs openpyxl)
```

Each run writes CSVs and a summary (`nav_summary.md`, `subline_summary.md`). To model a different facility, copy an
example file and change the inputs; the units are whatever you enter.

## Layout

| Path | Purpose |
|---|---|
| `src/fundfinancelab/nav_facility.py` | NAV facility: eligibility, LTV, breakeven drawdowns, cure, single-name stress |
| `src/fundfinancelab/subscription_line.py` | Subscription line: borrowing base, availability, coverage, investor scenarios |
| `src/fundfinancelab/cli.py` | Command line and summaries |
| `examples/` | Hypothetical inputs, including a facility with concentration and diversity covenants |
| `excel/` | The NAV model as a formula-driven workbook, and the script that builds it |
| `docs/explainer.md` | Subscription lines vs NAV loans: collateral, sizing, covenants, how agencies look at them, and where these models are simpler |
| `docs/model_spec.md` | Every formula the models use |
| `docs/limitations.md` | What the models leave out |
