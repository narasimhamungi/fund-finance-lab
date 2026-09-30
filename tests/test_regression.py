import csv
from decimal import Decimal
from pathlib import Path

import pytest

from fundfinancelab import regression as reg
from fundfinancelab.cli import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
CASES = ROOT / "excel" / "regression" / "cases.csv"
LO_LOG = ROOT / "excel" / "regression" / "libreoffice_log.csv"


@pytest.fixture(scope="module")
def rows():
    return reg.read_cases(CASES)


def _perfect_log(path: Path, rows) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(reg.LOG_COLUMNS)
        for r in rows:
            for f in reg.FIELDS:
                w.writerow([r["case_id"], f, r[f"exp_{f}"], "TRUE"])


def assert_same_cases(new, old):
    """Numbers compared to 1e-12 relative, not as text: Python 3.12 made sum() of floats compensated, so
    3.10/3.11 differ from the committed file (generated on 3.12) in the last digit. Text fields must match exactly."""
    assert [r["case_id"] for r in new] == [r["case_id"] for r in old]
    for a, b in zip(new, old):
        assert a.keys() == b.keys()
        for k in a:
            try:
                x, y = float(a[k]), float(b[k])
            except ValueError:
                assert a[k] == b[k], (a["case_id"], k)
            else:
                assert x == pytest.approx(y, rel=1e-12, abs=1e-12), (a["case_id"], k)


def test_committed_cases_match_a_fresh_generation(tmp_path):
    # Fails if the model or the generator changed without regenerating excel/regression/cases.csv.
    # Parsed, so Git line-ending conversion is harmless.
    fresh = tmp_path / "cases.csv"
    reg.write_cases(fresh, reg.all_cases(EXAMPLES))
    assert_same_cases(reg.read_cases(fresh), reg.read_cases(CASES))


def test_generation_is_deterministic():
    assert reg.random_cases(5, seed=7) == reg.random_cases(5, seed=7)
    assert reg.random_cases(5, seed=7) != reg.random_cases(5, seed=8)


def test_cases_cover_every_regime(rows):
    exp = lambda f: [r[f"exp_{f}"] for r in rows]  # noqa: E731
    assert set(exp("status")) == {"ok", "cash sweep", "breach"}
    assert any(float(x) > 0 for x in exp("excluded_single_cap"))
    assert any(float(x) > 0 for x in exp("excluded_top_n"))
    assert "FALSE" in exp("diversified")
    assert {"1.0", "0.5"} <= {r["single_name_loss"] for r in rows}
    assert any(r["loan"] == "0.0" for r in rows)
    assert any(r["top_n"] == "" for r in rows) and any(r["top_n"] != "" for r in rows)
    navs = [[r[f"nav_{i:02d}"] for i in range(1, reg.SLOTS + 1) if r[f"nav_{i:02d}"]] for r in rows]
    assert any(len(set(n)) < len(n) for n in navs)                      # ties present
    assert any(len(n) == reg.SLOTS for n in navs)                       # every slot used at least once


def test_boundary_cases_follow_the_at_or_above_rule(rows):
    by_id = {r["case_id"]: r for r in rows}
    assert by_id["E01"]["exp_ltv"] == "0.25" and by_id["E01"]["exp_status"] == "breach"
    assert by_id["E02"]["exp_ltv"] == "0.2" and by_id["E02"]["exp_status"] == "cash sweep"
    assert by_id["E03"]["exp_drawdown_to_breach"] == "1.0" and by_id["E03"]["exp_status"] == "ok"
    assert float(by_id["E06"]["exp_cure_to_target"]) == pytest.approx(260 - 0.15 * 800)


def test_inputs_are_short_decimals(rows):
    # Excel reads at most 15 significant digits from text; short decimals parse to the same double everywhere.
    for r in rows:
        for k in list(reg.INPUT_CELLS) + [f"nav_{i:02d}" for i in range(1, reg.SLOTS + 1)]:
            if r[k] != "":
                assert -Decimal(r[k]).as_tuple().exponent <= 4, (r["case_id"], k, r[k])


def test_no_field_needs_csv_quoting():
    # The VBA harness reads cases.csv with a plain Split on commas.
    for line in CASES.read_text(encoding="utf-8").splitlines():
        assert '"' not in line
        assert len(line.split(",")) == len(reg.INPUT_COLUMNS) + len(reg.FIELDS)


def test_every_case_has_at_least_four_assets(rows):
    for r in rows:
        assert sum(1 for i in range(1, reg.SLOTS + 1) if r[f"nav_{i:02d}"]) >= 4


def test_committed_libreoffice_log_verifies():
    result = reg.verify_log(CASES, LO_LOG)
    assert result["passed"], reg.report_text(result, LO_LOG.name)
    assert result["logged"] == result["checks"] == 48 * len(reg.FIELDS)


def test_verifier_passes_a_perfect_log(tmp_path, rows):
    log = tmp_path / "log.csv"
    _perfect_log(log, rows)
    assert reg.verify_log(CASES, log)["passed"]


def test_verifier_catches_every_failure_mode(tmp_path, rows):
    log = tmp_path / "log.csv"
    _perfect_log(log, rows)
    lines = log.read_text(encoding="utf-8").splitlines()
    header, body = lines[0], lines[1:]
    first = body[0].split(",")
    wrong = ",".join([first[0], first[1], "123456.0", "TRUE"])          # wrong value, macro claims a pass
    edited = [header, wrong] + body[2:] + [body[2], "Z99,ltv,0.1,TRUE"]  # drop one row, duplicate one, add a stray
    log.write_text("\n".join(edited) + "\n", encoding="utf-8")
    r = reg.verify_log(CASES, log)
    assert not r["passed"]
    assert len(r["missing"]) == 1 and len(r["duplicates"]) == 1 and r["unexpected"] == [("Z99", "ltv")]
    assert len(r["failures"]) == 1 and len(r["macro_disagreements"]) == 1


def test_matching_rules():
    assert reg.matches("ltv", "0.25", "0.2500000004")
    assert not reg.matches("ltv", "0.25", "0.250002")
    assert not reg.matches("ltv", "0.25", "n/a")
    assert reg.matches("diversified", "TRUE", "True") and reg.matches("diversified", "FALSE", "0")
    assert not reg.matches("status", "breach", "cash sweep")


def test_cell_map_points_at_the_labelled_cells():
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.load_workbook(ROOT / "excel" / "nav_facility_stress.xlsx")
    labels = {"Calc!C42": ("Calc", "B42", "Eligible NAV"), "Calc!C44": ("Calc", "B44", "LTV"),
              "Calc!C47": ("Calc", "B47", "Status"), "Calc!C49": ("Calc", "B49", "Uniform drawdown to breach level"),
              "'Single-name'!C42": ("Single-name", "B42", "Eligible NAV"),
              "'Single-name'!C46": ("Single-name", "B46", "Status"), "Checks!B12": ("Checks", "A12", "Overall"),
              "Inputs!C5": ("Inputs", "B5", "Loan outstanding (USD m)"), "Inputs!C13": ("Inputs", "B13",
                                                                                        "Single-name loss (share written off)")}
    cells = {ref for _, ref, _ in reg.OUTPUTS} | set(reg.INPUT_CELLS.values())
    for ref, (sheet, cell, text) in labels.items():
        assert ref in cells
        assert wb[sheet][cell].value == text, (ref, wb[sheet][cell].value)
    assert wb["Inputs"]["B16"].value == "Asset" and wb["Inputs"]["C16"].value == "NAV (USD m)"


def test_cli_writes_cases_and_verifies_logs(tmp_path, rows, capsys):
    out = tmp_path / "cases.csv"
    assert main(["regression-cases", "--examples", str(EXAMPLES), "--out", str(out)]) == 0
    assert_same_cases(reg.read_cases(out), reg.read_cases(CASES))
    assert main(["verify-log", "--cases", str(CASES), "--log", str(LO_LOG)]) == 0
    bad = tmp_path / "bad.csv"
    bad.write_text("case_id,field,actual,macro_pass\n", encoding="utf-8")
    assert main(["verify-log", "--cases", str(CASES), "--log", str(bad)]) == 1
    assert "FAIL" in capsys.readouterr().out
