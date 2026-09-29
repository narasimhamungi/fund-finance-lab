import pytest

from fundfinancelab.subscription_line import Investor, SubLine, borrowing_base, position, scenarios

RATES = {"included": 0.90, "designated": 0.60, "excluded": 0.0}
LINE = SubLine(facility_size=300, outstanding=180, advance_rates=RATES)
INV = [Investor("A", 200, 0.35, "included"), Investor("B", 150, 0.35, "included"),
       Investor("C", 70, 0.35, "included"), Investor("D", 80, 0.35, "included"),
       Investor("E", 80, 0.35, "designated"), Investor("F", 50, 0.35, "designated"),
       Investor("G", 40, 0.35, "designated"), Investor("H", 30, 0.35, "excluded")]


def test_borrowing_base_applies_advance_rates_to_uncalled_capital():
    bb, contrib = borrowing_base(INV, LINE)
    assert bb == pytest.approx(0.9 * 0.65 * 500 + 0.6 * 0.65 * 170)       # 292.5 + 66.3
    assert contrib["H"] == 0.0


def test_capacity_is_the_lower_of_facility_size_and_borrowing_base():
    p = position(INV, LINE)
    assert p["capacity"] == 300 and p["availability"] == pytest.approx(120)
    assert p["mandatory_prepayment"] == 0.0


def test_coverage_counts_all_obligated_investors():
    p = position(INV, LINE)
    assert p["uncalled_total"] == pytest.approx(455)                       # excluded investors still owe calls
    assert p["coverage"] == pytest.approx(455 / 180)


def test_exclusion_versus_default():
    rows = {r["scenario"].split(" (")[0]: r for r in scenarios(INV, LINE)}
    excl, dflt = rows["largest contributor excluded"], rows["largest contributor defaults"]
    assert excl["borrowing_base"] == pytest.approx(dflt["borrowing_base"])  # both leave the borrowing base
    assert excl["coverage"] == pytest.approx(455 / 180)                     # an excluded investor still funds calls
    assert dflt["coverage"] == pytest.approx(325 / 180)                     # a defaulting one does not


def test_mandatory_prepayment_when_borrowing_base_falls_below_outstanding():
    rows = {r["scenario"]: r for r in scenarios(INV, LINE)}
    two = rows["two largest contributors excluded"]
    assert two["borrowing_base"] == pytest.approx(154.05)
    assert two["mandatory_prepayment"] == pytest.approx(25.95)


def test_investor_cap_limits_single_contributions():
    capped = SubLine(300, 180, RATES, investor_cap_pct=0.25)
    bb, contrib = borrowing_base(INV, capped)
    assert contrib["A"] == pytest.approx(0.25 * 358.8)
    assert bb < 358.8


def test_unknown_category_is_an_error():
    with pytest.raises(ValueError, match="no advance rate"):
        borrowing_base([Investor("X", 10, 0, "unrated")], LINE)


def test_undrawn_line_has_no_coverage_ratio(tmp_path):
    import json
    from fundfinancelab.cli import main
    cfg = {"facility": {"facility_size": 100, "outstanding": 0, "advance_rates": RATES},
           "investors": [{"name": "A", "commitment": 50, "called_pct": 0.0, "category": "included"}]}
    p = tmp_path / "c.json"
    p.write_text(json.dumps(cfg))
    assert main(["subline", "--config", str(p), "--out", str(tmp_path / "o")]) == 0
    assert "n/a the outstanding loan" in (tmp_path / "o" / "subline_summary.md").read_text(encoding="utf-8")
