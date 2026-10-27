"""Test CLI report output.

Run from the project root with:
    python3.12 -m pytest tests/test_cli.py
"""

import sys

from src import cli


def test_main_saves_report_in_citation_reports(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["src.cli", "1998AJ....116.1009R"])
    monkeypatch.setattr(
        cli,
        "summarize_citing_papers",
        lambda bibcode, rows: {
            "target": {},
            "target_summary": {},
            "citing_papers": [],
        },
    )
    monkeypatch.setattr(cli, "render_report", lambda *args: "report html")

    cli.main()

    report_path = (
        tmp_path / "citation_reports" /
        "citation_report_1998AJ....116.1009R.html"
    )
    assert report_path.read_text(encoding="utf-8") == "report html"
