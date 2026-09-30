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
    top_n: int | None = None            # optional: the N largest assets together ...
    top_n_share: float | None = None    # ... count for at most this share of eligible NAV
    min_assets: int | None = None       # optional diversity covenant: fewer assets triggers a cash sweep

    def __post_init__(self):
        if not 0 < self.ltv_target <= self.ltv_sweep <= self.ltv_breach < 1:
            raise ValueError("need 0 < ltv_target <= ltv_sweep <= ltv_breach < 1")
        if not 0 < self.single_asset_cap <= 1:
            raise ValueError("single_asset_cap must be in (0, 1]")
        if self.loan < 0:
            raise ValueError("loan must be non-negative")
        if (self.top_n is None) != (self.top_n_share is None):
            raise ValueError("set top_n and top_n_share together")
        if self.top_n is not None and (self.top_n < 1 or not 0 < self.top_n_share <= 1):
            raise ValueError("top_n must be >= 1 and top_n_share in (0, 1]")
        if self.min_assets is not None and self.min_assets < 1:
            raise ValueError("min_assets must be >= 1")


def eligible_nav(assets: list[Asset], cap: float, top_n: int | None = None,
                 top_n_share: float | None = None) -> tuple[float, float]:
    """(eligible NAV, excluded amount), applying the limits in sequence:
    1. single-asset cap: each asset counts up to cap x total NAV (total before exclusions);
    2. top-N limit (optional): the N largest capped values count for at most top_n_share of the
       step-1 eligible NAV; the excess is excluded.
    Each limit is measured against the aggregate before that limit is applied (a simplification;
    facility definitions vary)."""
    total = sum(a.nav for a in assets)
    capped = sorted((min(a.nav, cap * total) for a in assets), reverse=True)
    eligible = sum(capped)
    if top_n is not None:
        eligible -= max(0.0, sum(capped[:top_n]) - top_n_share * eligible)
    return eligible, total - eligible


def _eligible(assets: list[Asset], f: "NavFacility") -> tuple[float, float]:
    return eligible_nav(assets, f.single_asset_cap, f.top_n, f.top_n_share)


def diversity_ok(assets: list[Asset], f: "NavFacility") -> bool:
    return f.min_assets is None or sum(1 for a in assets if a.nav > 0) >= f.min_assets


def ltv(loan: float, eligible: float) -> float:
    return float("inf") if eligible <= 0 else loan / eligible


def status(value: float, f: NavFacility, diversified: bool = True) -> str:
    if value >= f.ltv_breach:
        return "breach"
    if value >= f.ltv_sweep or not diversified:
        return "cash sweep"
    return "ok"


def sweep_reason(value: float, f: NavFacility, diversified: bool = True) -> str:
    reasons = [r for r, hit in (("LTV", f.ltv_sweep <= value < f.ltv_breach), ("diversity", not diversified)) if hit]
    return " and ".join(reasons)


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
        elig, excl = _eligible(stressed, f)
        v, div = ltv(f.loan, elig), diversity_ok(stressed, f)
        rows.append({"drawdown": d, "nav": sum(a.nav for a in stressed), "eligible_nav": elig, "excluded": excl,
                     "ltv": v, "status": status(v, f, div), "sweep_reason": sweep_reason(v, f, div), "diversified": div,
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
        elig, excl = _eligible(stressed, f)
        v, div = ltv(f.loan, elig), diversity_ok(stressed, f)
        rows.append({"assets_written_down": k, "names": ", ".join(a.name for a in ranked[:k]), "loss": loss,
                     "nav": sum(a.nav for a in stressed), "eligible_nav": elig, "excluded": excl, "ltv": v,
                     "status": status(v, f, div), "sweep_reason": sweep_reason(v, f, div), "diversified": div,
                     "cure_to_target": cure_amount(f.loan, elig, f.ltv_target) if v >= f.ltv_breach else 0.0,
                     "remaining_drawdown_to_breach": breakeven_drawdown(f.loan, elig, f.ltv_breach)})
    return rows


def summary(assets: list[Asset], f: NavFacility) -> dict:
    total = sum(a.nav for a in assets)
    elig, excl = _eligible(assets, f)
    after_cap, _ = eligible_nav(assets, f.single_asset_cap)
    base, div = ltv(f.loan, elig), diversity_ok(assets, f)
    largest = max(assets, key=lambda a: a.nav)
    return {"assets": len(assets), "total_nav": total, "eligible_nav": elig, "excluded": excl,
            "excluded_single_cap": total - after_cap, "excluded_top_n": after_cap - elig,
            "loan": f.loan, "ltv": base, "status": status(base, f, div),
            "largest_asset": largest.name, "largest_asset_share": largest.nav / total if total else None,
            "drawdown_to_sweep": breakeven_drawdown(f.loan, elig, f.ltv_sweep),
            "drawdown_to_breach": breakeven_drawdown(f.loan, elig, f.ltv_breach)}
