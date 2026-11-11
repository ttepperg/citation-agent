"""Test CLI report output.

Run from the project root with:
    python3.12 -m pytest tests/test_cli.py
"""

import json
import sys

from src import cli


def test_main_saves_report_in_citation_reports(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["src.cli", "2025A&A...695A.193P"])
    results = {
        "target": {
            "bibcode": "2025A&A...695A.193P",
            "title": "Café",
            "abstract": "An abstract.",
        },
        "target_summary": {
            "summary": "A résumé.",
            "metadata": {
                "model": "gpt-test",
                "temperature": 1,
                "prompt_version": "target-summary-v1",
                "response_id": "resp_target",
                "created_at": 1790000000,
            },
        },
        "citing_papers": [{
            "record": {"bibcode": "CITING", "title": "Citing paper"},
            "passages": ["A cited passage."],
            "summary": "It cites the target.",
            "summary_metadata": {
                "model": "gpt-test",
                "temperature": 1,
                "prompt_version": "citation-summary-v2",
                "response_id": "resp_citing",
                "created_at": 1790000001,
            },
        }],
    }
    monkeypatch.setattr(
        cli,
        "summarize_citing_papers",
        lambda bibcode, rows: results,
    )
    cli.main()

    report_directory = tmp_path / "citation_reports"
    report_path = report_directory / "citation_report_2025A%26A...695A.193P.html"
    assert "Café" in report_path.read_text(encoding="utf-8")

    json_path = report_directory / "citation_report_2025A%26A...695A.193P.json"
    json_text = json_path.read_text(encoding="utf-8")
    assert json.loads(json_text) == results
    assert "Café" in json_text
