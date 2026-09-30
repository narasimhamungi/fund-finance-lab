# VBA regression harness: specification

**Status: specified, not built.** You write the macro; this document is its contract. Do not list VBA on a CV
until acceptance tests A1 to A6 below pass in Excel.

## Why it exists

`excel/nav_facility_stress.xlsx` reproduces `src/fundfinancelab/nav_facility.py` in formulas. Its Checks sheet
compares the two on one input set only, and says so. `excel/regression/cases.csv` holds 48 input sets with the
Python model's expected outputs: the two shipped configs, ten hand-built edge cases (exact thresholds, ties, zero
loan, binding limits) and 36 seeded random cases. The harness runs the workbook on every case **inside Excel** and
logs every output, so the Excel implementation is tested across the input space rather than at one point.

LibreOffice already runs the same cases (`python excel/regression/run_libreoffice.py`): 912 of 912 checks pass,
log in `excel/regression/libreoffice_log.csv`. That first run found a defect in the workbook's own Checks sheet
(the breakeven identity failed for every portfolio already in breach and returned `#DIV/0!` for a zero loan);
the formula is fixed in `excel/build_nav_workbook.py`. The VBA harness is the Excel run of the same test.

## Files

| Path | Role |
|---|---|
| `excel/regression/cases.csv` | Input. One row per case: inputs, then `exp_<field>` for 19 outputs. Regenerate with `fund-finance-lab regression-cases` after any model change; a test fails if the committed file is stale. No field contains a comma or a quote. |
| `excel/regression/vba_log.csv` | Output. Header `case_id,field,actual,macro_pass`; exactly one row per case x field (912 rows). |
| `excel/vba/RegressionHarness.bas` | The module, exported as text so Git can diff it. |
| `excel/nav_facility_stress.xlsm` | The workbook with the module. The `.xlsx` stays as the formula-only version. |

## Cell contract

Inputs (write): `Inputs!C5` loan, `C6` sweep LTV, `C7` breach LTV, `C8` cure target, `C9` single-asset cap,
`C10` top-N count, `C11` top-N share, `C12` minimum assets, `C13` single-name loss; asset names `B17:B36`,
NAVs `C17:C36` (20 slots).

Outputs (read), in log order:

| Field | Cell | Kind |
|---|---|---|
| eligible_nav | `Calc!C42` | number |
| excluded_single_cap | `Calc!C43` | number |
| excluded_top_n | `Calc!C41` | number |
| ltv | `Calc!C44` | number |
| diversified | `Calc!C46` | TRUE/FALSE |
| status | `Calc!C47` | text |
| drawdown_to_sweep | `Calc!C48` | number |
| drawdown_to_breach | `Calc!C49` | number |
| cure_to_target | `Calc!C50` | number |
| k1_eligible_nav, k1_ltv, k1_status | `'Single-name'!C42`, `C43`, `C46` | number, number, text |
| k2_eligible_nav, k2_ltv, k2_status | `'Single-name'!H42`, `H43`, `H46` | number, number, text |
| k3_eligible_nav, k3_ltv, k3_status | `'Single-name'!M42`, `M43`, `M46` | number, number, text |
| checks_overall | `Checks!B12` | text, expected `ALL CHECKS PASS` |

The same map lives in `src/fundfinancelab/regression.py` (`INPUT_CELLS`, `OUTPUTS`); a test checks that the
labels next to these cells have not moved.

## What the macro must do

1. Save the current input values (`Inputs!C5:C13`, `B17:C36`) to an array in memory.
2. Read `cases.csv` from `ThisWorkbook.Path & "\regression\cases.csv"`, line by line (`Open ... For Input`,
   `Line Input`, `Split(line, ",")`). Map column names from the header row; do not hard-code column numbers.
3. For each case: clear `B17:C36`; write the terms and the assets. **A blank field means "off": write `Empty`,
   never 0** (`ISNUMBER(0)` is TRUE, so a 0 would switch the limit on). Recalculate (`Application.Calculate`).
4. Read each output cell. If `IsError(cell.Value)`, log the text `#ERROR` and count a failure; do not stop.
   Compare: numbers pass if `Abs(actual - expected) <= 1E-6`; text must match exactly; booleans as TRUE/FALSE.
5. Append one log row per field. Write numbers with `Trim(Str(x))`, which always uses a full stop; `CStr` follows
   Windows regional settings and can write a decimal comma.
6. Restore the saved inputs and recalculate, including after a runtime error (`On Error GoTo Cleanup`). Never
   leave the workbook on a test case.
7. Write `vba_log.csv`; show a summary: cases run, checks, failures, first failing case and field.

Speed: switch off `ScreenUpdating` during the loop and restore it in Cleanup. Size: roughly 120 to 180 lines.
Suggested procedures: `RunRegression` (public), `LoadCases`, `WriteInputs`, `ReadOutput`, `Matches`,
`SaveInputs` / `RestoreInputs`, `WriteLog`.

## Acceptance tests

| # | Test | Pass condition |
|---|---|---|
| A1 | Open the `.xlsm` fresh, enable macros, run `RunRegression` | Summary shows 48 cases, 912 checks, 0 failures |
| A2 | `fund-finance-lab verify-log --log excel/regression/vba_log.csv` | Prints PASS (independent re-check; also fails on skipped, duplicated or stray rows, or if the macro's own pass flag is wrong) |
| A3 | Mutation: change `Calc!C42` to `=C39`, rerun, then undo | Harness reports failures; verifier prints FAIL |
| A4 | After A1, look at `Checks!D19:D26` | All read `match` (inputs restored to the shipped config) |
| A5 | Delete one data row from `vba_log.csv`, rerun the verifier | Reports 1 missing and FAIL |
| A6 | Export the module after the last edit | `excel/vba/RegressionHarness.bas` matches the module in the `.xlsm` |

Record the Excel version and the A1 and A2 output in the README when done.

## What you can claim once A1 to A6 pass

"Wrote a VBA regression harness that tests an Excel credit-facility model against its Python implementation across
48 cases (912 checks), with an independent Python verifier of the macro's log."
Until then: Python, Excel formulas, and a regression suite verified in LibreOffice. No VBA.

## For a timed Excel/VBA test

Practise until you can write each without notes: loops over ranges and `Cells(r, c)`; reading and writing a block
through a Variant array (`arr = Range("A1:D100").Value`); `Application.Calculate` and calculation modes;
`On Error GoTo`; `Scripting.Dictionary`; a user-defined function; reading and writing a text file; a bisection
solver in a loop.
