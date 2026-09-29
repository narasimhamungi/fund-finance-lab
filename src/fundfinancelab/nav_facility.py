"""NAV facility: loan-to-value against a fund's portfolio, under portfolio drawdowns.

A NAV facility lends against the net asset value of the fund's investments. This model
computes eligible NAV after a single-asset concentration cap, LTV, the uniform drawdown
that reaches each covenant level, and the paydown (cure) needed to restore a target LTV.

All inputs are supplied by the user. The example files are hypothetical, not market terms.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    name: str
    nav: float


@dataclass(frozen=True)
class NavFacility:
    loan: float               # drawn amount
    ltv_sweep: float          # LTV at or above which a cash sweep applies
    ltv_breach: float         # LTV covenant: at or above this level the facility is in breach
    ltv_target: float         # LTV the borrower must restore to after a breach (cure)
    single_asset_cap: float   # an asset counts for at most this share of total NAV in eligible NAV

    def __post_init__(self):
        if not 0 < self.ltv_target <= self.ltv_sweep <= self.ltv_breach < 1:
            raise ValueError("need 0 < ltv_target <= ltv_sweep <= ltv_breach < 1")
        if not 0 < self.single_asset_cap <= 1:
            raise ValueError("single_asset_cap must be in (0, 1]")
        if self.loan < 0:
            raise ValueError("loan must be non-negative")


def eligible_nav(assets: list[Asset], cap: float) -> tuple[float, float]:
    """(eligible NAV, excluded excess). Each asset counts up to cap x total NAV, where total NAV
    is measured before exclusions (a simplification; facility definitions vary)."""
    total = sum(a.nav for a in assets)
    limit = cap * total
    eligible = sum(min(a.nav, limit) for a in assets)
    return eligible, total - eligible


def ltv(loan: float, eligible: float) -> float:
    return float("inf") if eligible <= 0 else loan / eligible


def status(value: float, f: NavFacility) -> str:
    if value >= f.ltv_breach:
        return "breach"
    if value >= f.ltv_sweep:
        return "cash sweep"
    return "ok"


def breakeven_drawdown(loan: float, eligible: float, level: float) -> float:
    """Uniform portfolio drawdown (0-1) at which LTV reaches `level`. A uniform drawdown scales
    eligible NAV proportionally because the cap is a share of total NAV. 0 if already there."""
    if eligible <= 0:
        return 0.0
    return max(0.0, 1.0 - loan / (level * eligible))


def cure_amount(loan: float, eligible: float, target: float) -> float:
    """Paydown (or equity injection used to repay) that restores LTV to `target`."""
    return max(0.0, loan - target * eligible)


def uniform_stress(assets: list[Asset], f: NavFacility, drawdowns: list[float]) -> list[dict]:
    rows = []
    for d in drawdowns:
        stressed = [Asset(a.name, a.nav * (1 - d)) for a in assets]
        elig, excl = eligible_nav(stressed, f.single_asset_cap)
        v = ltv(f.loan, elig)
        rows.append({"drawdown": d, "nav": sum(a.nav for a in stressed), "eligible_nav": elig, "excluded": excl,
                     "ltv": v, "status": status(v, f),
                     "cure_to_target": cure_amount(f.loan, elig, f.ltv_target) if v >= f.ltv_breach else 0.0})
    return rows


def single_name_stress(assets: list[Asset], f: NavFacility, loss: float = 1.0, names: int = 3) -> list[dict]:
    """Write down the k largest assets by `loss` (1.0 = total loss), for k = 1..names, with no
    change elsewhere. The concentration cap is recomputed on the smaller portfolio."""
    ranked = sorted(assets, key=lambda a: a.nav, reverse=True)
    rows = []
    for k in range(1, min(names, len(ranked)) + 1):
        hit = {a.name for a in ranked[:k]}
        stressed = [Asset(a.name, a.nav * (1 - loss)) if a.name in hit else a for a in assets]
        elig, excl = eligible_nav(stressed, f.single_asset_cap)
        v = ltv(f.loan, elig)
        rows.append({"assets_written_down": k, "names": ", ".join(a.name for a in ranked[:k]), "loss": loss,
                     "nav": sum(a.nav for a in stressed), "eligible_nav": elig, "excluded": excl, "ltv": v,
                     "status": status(v, f), "cure_to_target": cure_amount(f.loan, elig, f.ltv_target) if v >= f.ltv_breach else 0.0,
                     "remaining_drawdown_to_breach": breakeven_drawdown(f.loan, elig, f.ltv_breach)})
    return rows


def summary(assets: list[Asset], f: NavFacility) -> dict:
    total = sum(a.nav for a in assets)
    elig, excl = eligible_nav(assets, f.single_asset_cap)
    base = ltv(f.loan, elig)
    largest = max(assets, key=lambda a: a.nav)
    return {"assets": len(assets), "total_nav": total, "eligible_nav": elig, "excluded": excl,
            "loan": f.loan, "ltv": base, "status": status(base, f),
            "largest_asset": largest.name, "largest_asset_share": largest.nav / total if total else None,
            "drawdown_to_sweep": breakeven_drawdown(f.loan, elig, f.ltv_sweep),
            "drawdown_to_breach": breakeven_drawdown(f.loan, elig, f.ltv_breach)}
