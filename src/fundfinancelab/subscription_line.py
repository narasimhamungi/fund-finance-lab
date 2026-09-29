"""Subscription line: borrowing base against investors' uncalled commitments.

A subscription (capital call) facility is repaid from capital calls on the fund's investors.
The borrowing base counts each investor's uncalled commitment at an advance rate set by
its category. This model computes the borrowing base, availability, any mandatory
prepayment, and how those move when investors are excluded or default.

All inputs are supplied by the user. The example files are hypothetical, not market terms.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Investor:
    name: str
    commitment: float
    called_pct: float        # share of the commitment already called (0-1)
    category: str            # a key of SubLine.advance_rates, e.g. included / designated / excluded

    @property
    def uncalled(self) -> float:
        return self.commitment * (1.0 - self.called_pct)


@dataclass(frozen=True)
class SubLine:
    facility_size: float
    outstanding: float
    advance_rates: dict = field(default_factory=dict)
    investor_cap_pct: float | None = None   # max share of the (uncapped) borrowing base from one investor

    def rate(self, category: str) -> float:
        if category not in self.advance_rates:
            raise ValueError(f"no advance rate for investor category {category!r}")
        return self.advance_rates[category]


def borrowing_base(investors: list[Investor], line: SubLine) -> tuple[float, dict[str, float]]:
    """(borrowing base, contribution per investor). The optional cap is applied once, as a share of
    the uncapped borrowing base (a simplification; facility definitions vary)."""
    raw = {i.name: line.rate(i.category) * i.uncalled for i in investors}
    total = sum(raw.values())
    if line.investor_cap_pct is not None:
        limit = line.investor_cap_pct * total
        raw = {k: min(v, limit) for k, v in raw.items()}
    return sum(raw.values()), raw


def position(investors: list[Investor], line: SubLine) -> dict:
    bb, contrib = borrowing_base(investors, line)
    capacity = min(line.facility_size, bb)
    uncalled = sum(i.uncalled for i in investors)
    return {"borrowing_base": bb, "capacity": capacity,
            "availability": max(0.0, capacity - line.outstanding),
            "mandatory_prepayment": max(0.0, line.outstanding - capacity),
            "uncalled_total": uncalled,
            "coverage": (uncalled / line.outstanding) if line.outstanding else None,
            "call_needed_pct_of_uncalled": (line.outstanding / uncalled) if uncalled else None,
            "largest_contributor": max(contrib, key=contrib.get) if contrib else None,
            "largest_contribution_share": (max(contrib.values()) / bb) if bb else None}


def _exclude(investors: list[Investor], names: set[str], default: bool) -> list[Investor]:
    """Excluded investors drop out of the borrowing base. A defaulting investor also stops funding
    calls, so its uncalled commitment leaves coverage as well."""
    out = []
    for i in investors:
        if i.name in names:
            if default:
                continue
            out.append(Investor(i.name, i.commitment, i.called_pct, "excluded"))
        else:
            out.append(i)
    return out


def scenarios(investors: list[Investor], line: SubLine) -> list[dict]:
    if "excluded" not in line.advance_rates:
        line = SubLine(line.facility_size, line.outstanding, {**line.advance_rates, "excluded": 0.0},
                       line.investor_cap_pct)
    by_bb = sorted(investors, key=lambda i: line.rate(i.category) * i.uncalled, reverse=True)
    designated = {i.name for i in investors if i.category == "designated"}
    cases = [("base", set(), False),
             (f"largest contributor excluded ({by_bb[0].name})", {by_bb[0].name}, False),
             ("two largest contributors excluded", {i.name for i in by_bb[:2]}, False),
             ("all designated investors excluded", designated, False),
             (f"largest contributor defaults ({by_bb[0].name})", {by_bb[0].name}, True)]
    rows = []
    for label, names, default in cases:
        p = position(_exclude(investors, names, default), line)
        rows.append({"scenario": label, **p})
    return rows
