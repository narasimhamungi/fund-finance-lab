import pytest

from fundfinancelab.nav_facility import (Asset, NavFacility, breakeven_drawdown, cure_amount, eligible_nav, ltv,
                                         single_name_stress, status, summary, uniform_stress)

F = NavFacility(loan=150, ltv_sweep=0.20, ltv_breach=0.25, ltv_target=0.15, single_asset_cap=0.20)
ASSETS = [Asset("A", 240), Asset("B", 150), Asset("C", 120), Asset("D", 100), Asset("E", 90), Asset("F", 80),
          Asset("G", 70), Asset("H", 60), Asset("I", 40), Asset("J", 30), Asset("K", 20)]


def test_concentration_cap_excludes_the_excess():
    elig, excl = eligible_nav(ASSETS, 0.20)
    assert (elig, excl) == (960, 40)          # A counts for 200 of its 240


def test_ltv_and_status_bands():
    assert ltv(150, 960) == pytest.approx(0.15625)
    assert [status(x, F) for x in (0.19, 0.20, 0.249, 0.25)] == ["ok", "cash sweep", "cash sweep", "breach"]


def test_breakeven_drawdown_is_exact_under_uniform_stress():
    d = breakeven_drawdown(150, 960, 0.25)
    assert d == pytest.approx(0.375)
    row = uniform_stress(ASSETS, F, [d])[0]
    assert row["ltv"] == pytest.approx(0.25) and row["status"] == "breach"


def test_breakeven_is_zero_when_already_past_the_level():
    assert breakeven_drawdown(300, 960, 0.25) == 0.0


def test_cure_restores_target_ltv():
    cure = cure_amount(150, 576, 0.15)
    assert cure == pytest.approx(63.6)
    assert ltv(150 - cure, 576) == pytest.approx(0.15)


def test_cure_is_only_reported_in_breach():
    rows = {r["drawdown"]: r for r in uniform_stress(ASSETS, F, [0.25, 0.40])}
    assert rows[0.25]["status"] == "cash sweep" and rows[0.25]["cure_to_target"] == 0.0
    assert rows[0.40]["cure_to_target"] == pytest.approx(63.6)


def test_single_name_losses_recompute_the_cap():
    rows = single_name_stress(ASSETS, F, loss=1.0, names=3)
    assert [r["eligible_nav"] for r in rows] == pytest.approx([760, 610, 488])   # D is capped at 98 in the last case
    assert [r["status"] for r in rows] == ["ok", "cash sweep", "breach"]


def test_summary_reports_headroom_in_drawdown_terms():
    s = summary(ASSETS, F)
    assert s["drawdown_to_sweep"] == pytest.approx(1 - 150 / (0.20 * 960))
    assert s["largest_asset"] == "A" and s["largest_asset_share"] == pytest.approx(0.24)


@pytest.mark.parametrize("kwargs", [dict(ltv_target=0.30), dict(ltv_breach=1.2), dict(single_asset_cap=0), dict(loan=-1)])
def test_inconsistent_terms_are_rejected(kwargs):
    base = dict(loan=150, ltv_sweep=0.20, ltv_breach=0.25, ltv_target=0.15, single_asset_cap=0.20)
    with pytest.raises(ValueError):
        NavFacility(**{**base, **kwargs})
