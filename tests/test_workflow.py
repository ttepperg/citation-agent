"""Test citation workflow composition.

Run from the project root with:
    python3.12 -m pytest tests/test_workflow.py
"""

from src import workflow


def test_summarize_citing_papers_reports_total_and_keeps_summary_metadata(
    monkeypatch, capsys
):
    target = {
        "bibcode": "TARGET",
        "title": "Target paper",
        "author": ["Target, A."],
        "year": "2025",
    }
    citing = {"bibcode": "CITING", "title": "Citing paper", "year": "2026"}
    metadata = {
        "model": "gpt-6-astra-2026-08-15",
        "temperature": 1,
        "prompt_version": "citation-summary-v2",
        "response_id": "resp_test123",
        "created_at": 1790000000,
    }
    monkeypatch.setattr(workflow, "get_paper", lambda bibcode, token: target)
    monkeypatch.setattr(
        workflow, "get_citing_papers",
        lambda bibcode, token, rows: ([citing], 17),
    )
    monkeypatch.setattr(workflow, "normalise_record", lambda record: record)
    monkeypatch.setattr(
        workflow, "get_citation_passages",
        lambda target_record, paper, token: ["The target is used as a baseline."],
    )
    monkeypatch.setattr(
        workflow, "summarize_paper",
        lambda target_record, record, passages, api_key: {
            "summary": "It provides a baseline.",
            "metadata": metadata,
        },
    )

    result = workflow.summarize_citing_papers(
        "TARGET", token="ads-token", rows=1, api_key="openai-key"
    )

    assert result["citing_papers"] == [{
        "record": citing,
        "passages": ["The target is used as a baseline."],
        "summary": "It provides a baseline.",
        "summary_metadata": metadata,
    }]
    assert (
        "ADS found 17 citing papers; processing 1 (limit: 1)."
        in capsys.readouterr().out
    )
