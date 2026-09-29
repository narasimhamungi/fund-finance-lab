import json
from pathlib import Path

from fundfinancelab.cli import main

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_nav_cli_writes_outputs(tmp_path, capsys):
    assert main(["nav", "--config", str(EXAMPLES / "nav_facility_hypothetical.json"), "--out", str(tmp_path)]) == 0
    summary = (tmp_path / "nav_summary.md").read_text(encoding="utf-8")
    assert "Hypothetical inputs" in summary and "LTV 15.6% (ok)" in summary
    assert (tmp_path / "nav_uniform_stress.csv").exists() and (tmp_path / "nav_single_name_stress.csv").exists()


def test_subline_cli_writes_outputs(tmp_path):
    assert main(["subline", "--config", str(EXAMPLES / "subscription_line_hypothetical.json"), "--out", str(tmp_path)]) == 0
    summary = (tmp_path / "subline_summary.md").read_text(encoding="utf-8")
    assert "borrowing base 358.8" in summary and "2.53x" in summary


def test_bad_config_returns_error(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"facility": {"loan": 1, "ltv_sweep": 0.3, "ltv_breach": 0.2, "ltv_target": 0.1,
                                            "single_asset_cap": 0.2}, "assets": [{"name": "A", "nav": 1}]}))
    assert main(["nav", "--config", str(bad), "--out", str(tmp_path / "o")]) == 2
