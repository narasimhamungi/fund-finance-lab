"""fund-finance-lab nav|subline|coverage --config FILE.json --out DIR
   fund-finance-lab regression-cases | verify-log --log FILE.csv

Reads a JSON input file (see examples/), runs the stress and writes CSVs plus a summary.
Inputs are the user's; the example files are hypothetical, not market terms.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from . import nav_facility as nf
from . import regression as reg
from . import subscription_line as sl

DISCLAIMER = ("*Hypothetical inputs for illustration. Not observed market terms, not advice, and not any "
              "rating agency's methodology.*")


def _write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})


def _pct(x):
    return "n/a" if x is None else f"{x:.1%}"


def _num(x, units=""):
    return "n/a" if x is None else f"{x:,.1f}{(' ' + units) if units else ''}"


def run_nav(cfg: dict, out: Path) -> Path:
    f = nf.NavFacility(**cfg["facility"])
    assets = [nf.Asset(a["name"], float(a["nav"])) for a in cfg["assets"]]
    units = cfg.get("units", "")
    s = nf.summary(assets, f)
    uni = nf.uniform_stress(assets, f, cfg.get("drawdowns", [i / 20 for i in range(11)]))
    names = nf.single_name_stress(assets, f, cfg.get("single_name_loss", 1.0), cfg.get("single_names", 3))
    out.mkdir(parents=True, exist_ok=True)
    _write_csv(out / "nav_uniform_stress.csv", uni)
    _write_csv(out / "nav_single_name_stress.csv", names)
    first_breach = next((r["drawdown"] for r in uni if r["status"] == "breach"), None)
    L = [f"# NAV facility stress: {cfg.get('label', 'unnamed')}", "", DISCLAIMER, "",
         f"Units: {units or 'as supplied'}", "",
         "## Position",
         f"- Total NAV {_num(s['total_nav'])}; eligible NAV {_num(s['eligible_nav'])} after concentration limits "
         f"(excluded {_num(s['excluded_single_cap'])} by the {f.single_asset_cap:.0%} single-asset cap"
         + (f", {_num(s['excluded_top_n'])} by the top-{f.top_n} limit" if f.top_n else "")
         + f"); largest asset {s['largest_asset']} at {_pct(s['largest_asset_share'])} of NAV",
         f"- Loan {_num(f.loan)}; LTV {_pct(s['ltv'])} ({s['status']}); cash sweep at {_pct(f.ltv_sweep)}, "
         f"breach at {_pct(f.ltv_breach)}, cure target {_pct(f.ltv_target)}",
         f"- Uniform drawdown to reach the sweep level: {_pct(s['drawdown_to_sweep'])}; to reach breach: {_pct(s['drawdown_to_breach'])}",
         *( [f"- Concentration limit: the {f.top_n} largest assets count for at most {f.top_n_share:.0%} of eligible NAV"]
            if f.top_n else [] ),
         *( [f"- Diversity covenant: fewer than {f.min_assets} assets with value triggers a cash sweep"] if f.min_assets else [] ),
         "", "## Uniform drawdowns (`nav_uniform_stress.csv`)",
         "| Drawdown | Eligible NAV | LTV | Status | Cure to target |", "|---|---|---|---|---|"]
    for r in uni:
        L.append(f"| {r['drawdown']:.0%} | {_num(r['eligible_nav'])} | {_pct(r['ltv'])} | {r['status']} | {_num(r['cure_to_target'])} |")
    L += ["", f"First grid point in breach: {_pct(first_breach) if first_breach is not None else 'none on this grid'}.",
          "", f"## Largest assets written down by {cfg.get('single_name_loss', 1.0):.0%} (`nav_single_name_stress.csv`)",
          "| Assets | Names | Eligible NAV | LTV | Status | Further uniform drawdown to breach |", "|---|---|---|---|---|---|"]
    for r in names:
        st = r["status"]
        if st == "cash sweep" and r["sweep_reason"]:
            st = f"cash sweep ({r['sweep_reason']})"
        elif st == "breach" and not r["diversified"]:
            st = "breach (diversity also failed)"
        L.append(f"| {r['assets_written_down']} | {r['names']} | {_num(r['eligible_nav'])} | {_pct(r['ltv'])} | {st} | "
                 f"{_pct(r['remaining_drawdown_to_breach'])} |")
    L += ["", "Limits: see docs/limitations.md. Each concentration limit is measured against the aggregate before it "
          "is applied; valuation lag, FX and cross-default terms are not modelled."]
    (out / "nav_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return out


def run_subline(cfg: dict, out: Path) -> Path:
    line = sl.SubLine(**cfg["facility"])
    investors = [sl.Investor(i["name"], float(i["commitment"]), float(i["called_pct"]), i["category"])
                 for i in cfg["investors"]]
    rows = sl.scenarios(investors, line)
    out.mkdir(parents=True, exist_ok=True)
    _write_csv(out / "subline_scenarios.csv", rows)
    base = rows[0]
    L = [f"# Subscription line stress: {cfg.get('label', 'unnamed')}", "", DISCLAIMER, "",
         f"Units: {cfg.get('units') or 'as supplied'}", "",
         "## Position",
         f"- Facility {_num(line.facility_size)}; outstanding {_num(line.outstanding)}; borrowing base {_num(base['borrowing_base'])}; "
         f"availability {_num(base['availability'])}",
         f"- Uncalled commitments {_num(base['uncalled_total'])}: "
         f"{'n/a' if base['coverage'] is None else format(base['coverage'], '.2f') + 'x'} the outstanding loan; a call of "
         f"{_pct(base['call_needed_pct_of_uncalled'])} of uncalled capital repays it",
         f"- Largest contributor to the borrowing base: {base['largest_contributor']} ({_pct(base['largest_contribution_share'])})",
         "", "## Scenarios (`subline_scenarios.csv`)",
         "| Scenario | Borrowing base | Mandatory prepayment | Coverage | Call needed |", "|---|---|---|---|---|"]
    for r in rows:
        cov = "n/a" if r["coverage"] is None else f"{r['coverage']:.2f}x"
        L.append(f"| {r['scenario']} | {_num(r['borrowing_base'])} | {_num(r['mandatory_prepayment'])} | {cov} | "
                 f"{_pct(r['call_needed_pct_of_uncalled'])} |")
    L += ["", "Limits: see docs/limitations.md. Exclusion events, cure periods and investor-level concentration terms "
          "are simplified."]
    (out / "subline_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return out


def run_coverage(cfg: dict, out: Path) -> Path:
    from . import asset_coverage as ac
    lv = ac.Leverage(**cfg["leverage"])
    tests = cfg.get("tests", {"debt_min": 3.0, "total_min": 2.0, "contractual_total_min": None})
    contractual = tests.get("contractual_total_min")
    units = cfg.get("units", "")
    rows = [
        {"measure": "Coverage assets (net assets + debt + preferred)", "value": lv.coverage_assets},
        {"measure": "Debt coverage (statutory minimum 300%)", "value": ac.debt_coverage(lv)},
        {"measure": "Total coverage, debt + preferred (statutory minimum 200%)", "value": ac.total_coverage(lv)},
        {"measure": "Reported-style coverage per $1,000 of debt", "value": None if not lv.debt else ac.debt_coverage(lv) * 1000},
        {"measure": "Reported-style coverage per $25 preferred (A / preferred x 25)", "value": ac.per_share_convention(lv)},
        {"measure": "Fall in coverage assets to 300% debt coverage", "value": ac.decline_to(lv, tests["debt_min"], "debt")},
        {"measure": "Fall in coverage assets to 200% total coverage", "value": ac.decline_to(lv, tests["total_min"], "total")},
    ]
    if contractual:
        rows.append({"measure": f"Fall in coverage assets to {contractual:.0%} contractual total coverage",
                     "value": ac.decline_to(lv, contractual, "total")})
    rows.append({"measure": "Common distribution capacity under the binding test",
                 "value": ac.distribution_capacity(lv, tests["debt_min"], max(tests["total_min"], contractual or 0))})
    out.mkdir(parents=True, exist_ok=True)
    _write_csv(out / "coverage.csv", rows)
    L = [f"# Asset coverage: {cfg.get('label', 'unnamed')}", "", f"Source: {cfg.get('source', 'as supplied')}",
         f"Units: {units or 'as supplied'}", "", "| Measure | Value |", "|---|---|"]
    for r in rows:
        v = r["value"]
        if v is None:
            txt = "n/a"
        elif "coverage (" in r["measure"] or r["measure"].startswith(("Debt coverage", "Total coverage")):
            txt = f"{v:.1%}"
        elif r["measure"].startswith("Fall"):
            txt = f"{v:.1%}"
        else:
            txt = f"{v:,.1f}"
        L.append(f"| {r['measure']} | {txt} |")
    L += ["", "The per-$25 preferred figure divides by the preferred amount alone; it is not the statutory preferred "
          "test, which divides by debt plus preferred. See docs/cef_coverage_memo.md."]
    (out / "coverage_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="fund-finance-lab")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, helptext in (("nav", "NAV facility LTV stress"), ("subline", "subscription line borrowing-base stress"),
                           ("coverage", "closed-end fund asset coverage (section 18)")):
        s = sub.add_parser(name, help=helptext)
        s.add_argument("--config", required=True, help="JSON input file (see examples/)")
        s.add_argument("--out", default=f"outputs/{name}", help="output directory")
    s = sub.add_parser("regression-cases", help="write workbook regression cases with Python-expected outputs")
    s.add_argument("--examples", default="examples", help="folder holding the shipped NAV configs")
    s.add_argument("--out", default="excel/regression/cases.csv", help="CSV to write")
    s.add_argument("--random", type=int, default=36, help="number of seeded random cases")
    s.add_argument("--seed", type=int, default=reg.SEED)
    s = sub.add_parser("verify-log", help="check a spreadsheet run's log against the regression cases")
    s.add_argument("--cases", default="excel/regression/cases.csv")
    s.add_argument("--log", required=True, help="log written by the VBA harness or the LibreOffice runner")
    args = p.parse_args(argv)
    if args.cmd == "regression-cases":
        cases = reg.all_cases(Path(args.examples), args.random, args.seed)
        reg.write_cases(Path(args.out), cases)
        print(f"{len(cases)} regression cases written to {args.out}")
        return 0
    if args.cmd == "verify-log":
        result = reg.verify_log(Path(args.cases), Path(args.log))
        print(reg.report_text(result, args.log), end="")
        return 0 if result["passed"] else 1
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    try:
        out = {"nav": run_nav, "subline": run_subline, "coverage": run_coverage}[args.cmd](cfg, Path(args.out))
    except (KeyError, TypeError, ValueError) as e:
        print(f"error in {args.config}: {e}")
        return 2
    print(f"{args.cmd} stress written to {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
