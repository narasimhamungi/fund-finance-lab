"""Regression cases for the NAV workbook, and a verifier for spreadsheet runs.

The workbook (excel/nav_facility_stress.xlsx) reproduces nav_facility.py in formulas, but its
Checks sheet cross-checks one input set only. This module writes many input sets together with
the Python model's expected outputs (excel/regression/cases.csv). A spreadsheet run - the VBA
harness in Excel (docs/vba_regression_harness.md) or the LibreOffice runner - loads each case,
recalculates, and logs what the workbook produced. verify_log() then checks that log against
the expected values, independently of whatever comparison the macro did itself.

Inputs are generated, not observed: they exercise the formulas and are not market terms.
"""
from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path

from . import nav_facility as nf

SEED = 20260930
TOL = 1e-6            # absolute tolerance for numeric fields
SLOTS = 20            # asset rows on the Inputs sheet
PASS_TEXT = "ALL CHECKS PASS"

# Workbook cell map. Must match excel/build_nav_workbook.py.
INPUT_CELLS = {"loan": "Inputs!C5", "ltv_sweep": "Inputs!C6", "ltv_breach": "Inputs!C7",
               "ltv_target": "Inputs!C8", "single_asset_cap": "Inputs!C9", "top_n": "Inputs!C10",
               "top_n_share": "Inputs!C11", "min_assets": "Inputs!C12", "single_name_loss": "Inputs!C13"}
NAME_CELLS = [f"Inputs!B{r}" for r in range(17, 17 + SLOTS)]
NAV_CELLS = [f"Inputs!C{r}" for r in range(17, 17 + SLOTS)]
OUTPUTS = [  # (field, cell, kind) - kind is num, bool or text
    ("eligible_nav", "Calc!C42", "num"),
    ("excluded_single_cap", "Calc!C43", "num"),
    ("excluded_top_n", "Calc!C41", "num"),
    ("ltv", "Calc!C44", "num"),
    ("diversified", "Calc!C46", "bool"),
    ("status", "Calc!C47", "text"),
    ("drawdown_to_sweep", "Calc!C48", "num"),
    ("drawdown_to_breach", "Calc!C49", "num"),
    ("cure_to_target", "Calc!C50", "num"),
] + [(f"k{k}_{name}", f"'Single-name'!{col}{row}", kind)
     for k, col in ((1, "C"), (2, "H"), (3, "M"))
     for name, row, kind in (("eligible_nav", 42, "num"), ("ltv", 43, "num"), ("status", 46, "text"))] + [
    ("checks_overall", "Checks!B12", "text"),
]
FIELDS = [f for f, _, _ in OUTPUTS]
KIND = {f: k for f, _, k in OUTPUTS}
INPUT_COLUMNS = (["case_id", "description"] + list(INPUT_CELLS)
                 + [f"name_{i:02d}" for i in range(1, SLOTS + 1)] + [f"nav_{i:02d}" for i in range(1, SLOTS + 1)])
LOG_COLUMNS = ["case_id", "field", "actual", "macro_pass"]


# ------------------------------------------------------------------ cases
def _case(case_id: str, description: str, facility: dict, navs: list[float], loss: float) -> dict:
    if not 4 <= len(navs) <= SLOTS:
        raise ValueError(f"{case_id}: need 4 to {SLOTS} assets (the k = 3 block must leave one standing)")
    case = {"case_id": case_id, "description": description, "single_name_loss": loss,
            "loan": facility["loan"], "ltv_sweep": facility["ltv_sweep"], "ltv_breach": facility["ltv_breach"],
            "ltv_target": facility["ltv_target"], "single_asset_cap": facility["single_asset_cap"],
            "top_n": facility.get("top_n"), "top_n_share": facility.get("top_n_share"),
            "min_assets": facility.get("min_assets")}
    for i in range(SLOTS):
        case[f"name_{i + 1:02d}"] = f"Asset {i + 1:02d}" if i < len(navs) else None
        case[f"nav_{i + 1:02d}"] = navs[i] if i < len(navs) else None
    _facility(case)                                   # validates the terms
    return case


def _facility(case: dict) -> nf.NavFacility:
    return nf.NavFacility(loan=case["loan"], ltv_sweep=case["ltv_sweep"], ltv_breach=case["ltv_breach"],
                          ltv_target=case["ltv_target"], single_asset_cap=case["single_asset_cap"],
                          top_n=case["top_n"], top_n_share=case["top_n_share"], min_assets=case["min_assets"])


def _assets(case: dict) -> list[nf.Asset]:
    return [nf.Asset(case[f"name_{i:02d}"], case[f"nav_{i:02d}"])
            for i in range(1, SLOTS + 1) if case[f"nav_{i:02d}"] is not None]


def shipped_cases(examples: Path) -> list[dict]:
    out = []
    for i, fname in enumerate(("nav_facility_hypothetical.json", "nav_facility_covenants_hypothetical.json"), 1):
        cfg = json.loads((examples / fname).read_text(encoding="utf-8"))
        out.append(_case(f"S{i:02d}", f"shipped config {fname}", cfg["facility"],
                         [float(a["nav"]) for a in cfg["assets"]], float(cfg.get("single_name_loss", 1.0))))
    return out


def edge_cases() -> list[dict]:
    """Hand-built cases at the places formulas usually break: exact thresholds, ties, zero loan."""
    terms = {"ltv_sweep": 0.20, "ltv_breach": 0.25, "ltv_target": 0.15, "single_asset_cap": 0.20}
    ten = [80.0] * 10                                              # total 800, cap 160, nothing capped
    return [
        _case("E01", "LTV exactly at the breach level (200 / 800 = 0.25)", {**terms, "loan": 200.0}, ten, 1.0),
        _case("E02", "LTV exactly at the sweep level (160 / 800 = 0.20)", {**terms, "loan": 160.0}, ten, 1.0),
        _case("E03", "zero loan: LTV 0 and drawdowns to each level are 100%", {**terms, "loan": 0.0}, ten, 1.0),
        _case("E04", "ties at the cap and at the top-N boundary",
              {**terms, "loan": 120.0, "single_asset_cap": 0.15, "top_n": 3, "top_n_share": 0.40},
              [200.0, 200.0, 200.0, 90.0, 90.0, 60.0, 40.0], 1.0),
        _case("E05", "diversity covenant fails while LTV is low (sweep for diversity only)",
              {**terms, "loan": 60.0, "min_assets": 12}, ten, 1.0),
        _case("E06", "already in breach: cure to target is positive", {**terms, "loan": 260.0}, ten, 1.0),
        _case("E07", "tight single-asset cap binds on most assets",
              {**terms, "loan": 90.0, "single_asset_cap": 0.06},
              [150.0, 120.0, 110.0, 95.0, 80.0, 60.0, 45.0, 30.0, 20.0, 15.0, 10.0, 5.0], 1.0),
        _case("E08", "top-N limit binds hard", {**terms, "loan": 110.0, "single_asset_cap": 0.50,
                                                "top_n": 2, "top_n_share": 0.30},
              [300.0, 250.0, 60.0, 50.0, 40.0, 30.0, 20.0], 1.0),
        _case("E09", "partial single-name loss (50%)", {**terms, "loan": 150.0}, [240.0, 150.0, 120.0, 100.0,
                                                                                    90.0, 80.0, 70.0, 60.0], 0.5),
        _case("E10", "all 20 slots filled with both optional limits on",
              {**terms, "loan": 180.0, "top_n": 5, "top_n_share": 0.55, "min_assets": 15},
              [float(x) for x in range(100, 0, -5)], 1.0),
    ]


def random_cases(n: int, seed: int = SEED) -> list[dict]:
    """Seeded cases across the input space. Inputs are rounded to 2-4 decimals so the text in the CSV
    parses to the same double in Python and in Excel."""
    rng = random.Random(seed)
    out = []
    for i in range(1, n + 1):
        count = rng.randint(4, SLOTS)
        navs = [round(rng.lognormvariate(4.0, 0.8), 2) for _ in range(count)]
        if rng.random() < 0.25:                                    # plant a tie
            navs[rng.randrange(count)] = navs[0]
        target = round(rng.uniform(0.05, 0.20), 4)
        sweep = round(target + rng.uniform(0.0, 0.10), 4)
        breach = round(sweep + rng.uniform(0.01, 0.10), 4)
        terms = {"ltv_target": target, "ltv_sweep": sweep, "ltv_breach": breach, "loan": 0.0,
                 "single_asset_cap": rng.choice([0.08, 0.10, 0.15, 0.20, 0.25, 0.35, 0.50, 1.0])}
        if rng.random() < 0.5:
            terms["top_n"], terms["top_n_share"] = rng.randint(1, 8), round(rng.uniform(0.30, 0.90), 4)
        if rng.random() < 0.5:
            terms["min_assets"] = rng.randint(3, 15)
        probe = _case("probe", "", terms, navs, 1.0)
        eligible, _ = nf.eligible_nav(_assets(probe), terms["single_asset_cap"], terms.get("top_n"),
                                      terms.get("top_n_share"))
        terms["loan"] = round(rng.uniform(0.03, 0.50) * eligible, 2)
        loss = rng.choice([1.0, 1.0, 0.75, 0.5, 0.3])
        out.append(_case(f"R{i:02d}", f"random seed {seed} draw {i}", terms, navs, loss))
    return out


def all_cases(examples: Path, n_random: int = 36, seed: int = SEED) -> list[dict]:
    return shipped_cases(examples) + edge_cases() + random_cases(n_random, seed)


# ------------------------------------------------------------------ expected values
def expected(case: dict) -> dict:
    f, assets = _facility(case), _assets(case)
    s = nf.summary(assets, f)
    out = {"eligible_nav": s["eligible_nav"], "excluded_single_cap": s["excluded_single_cap"],
           "excluded_top_n": s["excluded_top_n"], "ltv": s["ltv"], "diversified": nf.diversity_ok(assets, f),
           "status": s["status"], "drawdown_to_sweep": s["drawdown_to_sweep"],
           "drawdown_to_breach": s["drawdown_to_breach"],
           "cure_to_target": nf.cure_amount(f.loan, s["eligible_nav"], f.ltv_target) if s["ltv"] >= f.ltv_breach else 0.0}
    for row in nf.single_name_stress(assets, f, loss=case["single_name_loss"], names=3):
        k = row["assets_written_down"]
        out[f"k{k}_eligible_nav"], out[f"k{k}_ltv"], out[f"k{k}_status"] = row["eligible_nav"], row["ltv"], row["status"]
    out["checks_overall"] = PASS_TEXT
    return out


def _text(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        return repr(v)
    return str(v)


def write_cases(path: Path, cases: list[dict]) -> None:
    """One row per case: inputs, then exp_<field> for every output. No field contains a comma or a quote,
    so a macro can read the file with a plain Split on commas."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(INPUT_COLUMNS + [f"exp_{f}" for f in FIELDS])
        for c in cases:
            e = expected(c)
            w.writerow([_text(c[k]) for k in INPUT_COLUMNS] + [_text(e[f]) for f in FIELDS])


def read_cases(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def case_inputs(row: dict) -> dict:
    """Typed inputs from a cases.csv row (blank = off / empty slot)."""
    def num(k, cast=float):
        return cast(row[k]) if row[k] != "" else None
    case = {"case_id": row["case_id"], "description": row["description"],
            "loan": num("loan"), "ltv_sweep": num("ltv_sweep"), "ltv_breach": num("ltv_breach"),
            "ltv_target": num("ltv_target"), "single_asset_cap": num("single_asset_cap"),
            "top_n": num("top_n", int), "top_n_share": num("top_n_share"), "min_assets": num("min_assets", int),
            "single_name_loss": num("single_name_loss")}
    for i in range(1, SLOTS + 1):
        case[f"name_{i:02d}"] = row[f"name_{i:02d}"] or None
        case[f"nav_{i:02d}"] = num(f"nav_{i:02d}")
    return case


# ------------------------------------------------------------------ comparison and verification
def _as_bool(v: str) -> bool | None:
    t = str(v).strip().upper()
    return {"TRUE": True, "FALSE": False, "1": True, "0": False, "-1": True}.get(t)


def matches(field: str, expected_text: str, actual_text: str) -> bool:
    kind = KIND[field]
    if kind == "num":
        try:
            e, a = float(expected_text), float(actual_text)
        except ValueError:
            return False
        if math.isinf(e):
            return math.isinf(a)
        return math.isfinite(a) and abs(a - e) <= TOL
    if kind == "bool":
        a = _as_bool(actual_text)
        return a is not None and a == _as_bool(expected_text)
    return str(actual_text).strip() == str(expected_text).strip()


def verify_log(cases_path: Path, log_path: Path) -> dict:
    """Check a spreadsheet run's log against cases.csv. Every case x field must appear exactly once;
    a missing, duplicated or unexpected row is a failure, not a skip."""
    cases = read_cases(cases_path)
    exp = {(r["case_id"], f): r[f"exp_{f}"] for r in cases for f in FIELDS}
    seen: dict[tuple[str, str], dict] = {}
    duplicates, unexpected = [], []
    with open(log_path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            key = (row["case_id"].strip(), row["field"].strip())
            if key not in exp:
                unexpected.append(key)
            elif key in seen:
                duplicates.append(key)
            else:
                seen[key] = row
    missing = [k for k in exp if k not in seen]
    failures, disagreements = [], []
    for key, row in seen.items():
        ok = matches(key[1], exp[key], row["actual"])
        if not ok:
            failures.append({"case_id": key[0], "field": key[1], "expected": exp[key], "actual": row["actual"]})
        macro = _as_bool(row.get("macro_pass", ""))
        if macro is not None and macro != ok:
            disagreements.append(key)
    passed = not (missing or duplicates or unexpected or failures or disagreements)
    return {"passed": passed, "cases": len(cases), "checks": len(exp), "logged": len(seen), "missing": missing,
            "duplicates": duplicates, "unexpected": unexpected, "failures": failures,
            "macro_disagreements": disagreements}


def report_text(r: dict, log_name: str) -> str:
    lines = [f"Verification of {log_name}: {'PASS' if r['passed'] else 'FAIL'}",
             f"- {r['cases']} cases x {len(FIELDS)} fields = {r['checks']} checks; {r['logged']} logged",
             f"- missing {len(r['missing'])}, duplicated {len(r['duplicates'])}, unexpected {len(r['unexpected'])}",
             f"- value mismatches {len(r['failures'])} (tolerance {TOL:g} absolute for numbers)",
             f"- rows where the macro's own pass flag disagrees with this check: {len(r['macro_disagreements'])}"]
    for f in r["failures"][:20]:
        lines.append(f"  - {f['case_id']} {f['field']}: expected {f['expected']}, got {f['actual']}")
    return "\n".join(lines) + "\n"
