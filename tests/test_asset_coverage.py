import pytest

from fundfinancelab.asset_coverage import (Leverage, debt_coverage, decline_to, deleveraging_to_restore,
                                           distribution_capacity, per_share_convention, total_coverage)

# Calamos Strategic Total Return Fund, FY2021 financial highlights (USD thousands)
CSQ = Leverage(net_assets_common=2_928_463, debt=880_000, preferred=304_000)


def test_reproduces_the_fund_reported_coverage():
    assert round(debt_coverage(CSQ) * 1000) == 4673          # reported: $4,673 per $1,000 of loan
    assert round(per_share_convention(CSQ)) == 338           # reported: $338 per $25 MRPS


def test_statutory_preferred_test_is_far_lower_than_the_per_share_figure():
    assert total_coverage(CSQ) == pytest.approx(4_112_463 / 1_184_000)   # about 347%
    assert per_share_convention(CSQ) / 25 > 13                           # the per-share line implies 13.5x


def test_decline_to_threshold_lands_exactly_on_it():
    x = decline_to(CSQ, 2.25)
    stressed = Leverage(CSQ.net_assets_common - x * CSQ.coverage_assets, CSQ.debt, CSQ.preferred)
    assert total_coverage(stressed) == pytest.approx(2.25)


def test_deleveraging_restores_coverage_exactly():
    weak = Leverage(net_assets_common=1_000, debt=800, preferred=300)     # total coverage 1.909x
    r = deleveraging_to_restore(weak, 2.25)
    a, s = weak.coverage_assets - r, weak.senior - r
    assert a / s == pytest.approx(2.25)
    assert deleveraging_to_restore(CSQ, 2.25) == 0.0


def test_distribution_capacity_respects_the_binding_test():
    cap = distribution_capacity(CSQ, debt_min=3.0, total_min=2.25)
    assert cap == pytest.approx(CSQ.coverage_assets - max(3.0 * 880_000, 2.25 * 1_184_000))


def test_no_leverage_means_no_ratio():
    lv = Leverage(100, 0, 0)
    assert debt_coverage(lv) is None and total_coverage(lv) is None and decline_to(lv, 2.0) is None


def test_negative_amounts_rejected():
    with pytest.raises(ValueError):
        Leverage(-1, 0, 0)
