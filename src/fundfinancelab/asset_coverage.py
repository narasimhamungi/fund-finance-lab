"""Asset coverage for a leveraged closed-end fund (Investment Company Act section 18).

Coverage assets A = total assets less liabilities not represented by senior securities
                  = net assets to common shareholders + debt + preferred (liquidation value).
Debt coverage   = A / debt                      (statutory minimum 300%)
Total coverage  = A / (debt + preferred)        (statutory preferred test, minimum 200%)
Contractual tests (e.g. a 225% preferred-share covenant) are inputs.

Funds also report coverage "per $25 preferred share" by dividing A by the preferred
amount alone. That convention is not the statutory preferred test; both are shown.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Leverage:
    net_assets_common: float
    debt: float
    preferred: float           # liquidation preference outstanding

    def __post_init__(self):
        if min(self.net_assets_common, self.debt, self.preferred) < 0:
            raise ValueError("amounts must be non-negative")

    @property
    def coverage_assets(self) -> float:
        return self.net_assets_common + self.debt + self.preferred

    @property
    def senior(self) -> float:
        return self.debt + self.preferred


def debt_coverage(lv: Leverage) -> float | None:
    return None if lv.debt == 0 else lv.coverage_assets / lv.debt


def total_coverage(lv: Leverage) -> float | None:
    return None if lv.senior == 0 else lv.coverage_assets / lv.senior


def per_share_convention(lv: Leverage, per: float = 25.0) -> float | None:
    """Coverage 'per $25 liquidation value' as funds commonly report it: A / preferred x 25."""
    return None if lv.preferred == 0 else lv.coverage_assets / lv.preferred * per


def decline_to(lv: Leverage, level: float, basis: str = "total") -> float | None:
    """Fall in coverage assets (share of A) that takes coverage down to `level`, with senior
    securities unchanged. 0 if already at or below it."""
    denom = lv.senior if basis == "total" else lv.debt
    if denom == 0:
        return None
    return max(0.0, 1.0 - level * denom / lv.coverage_assets)


def deleveraging_to_restore(lv: Leverage, level: float, basis: str = "total") -> float:
    """Senior securities to repay out of assets so that coverage returns to `level`.
    Repaying R lowers both A and the senior amount: (A - R) / (S - R) = level
    gives R = (level x S - A) / (level - 1)."""
    s = lv.senior if basis == "total" else lv.debt
    return max(0.0, (level * s - lv.coverage_assets) / (level - 1.0))


def distribution_capacity(lv: Leverage, debt_min: float = 3.0, total_min: float = 2.0) -> float:
    """Largest common distribution that keeps both tests met after paying it (the section 18
    dividend blockers, or stricter contractual levels passed in as total_min)."""
    need = max(debt_min * lv.debt, total_min * lv.senior)
    return max(0.0, lv.coverage_assets - need)
