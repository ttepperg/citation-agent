"""Test citation workflow composition.

Run from the project root with:
    python3.12 -m pytest tests/test_workflow.py
"""

from unittest.mock import Mock

from src import workflow


def test_summarize_citing_papers_reports_progress_and_keeps_summary_metadata(
    monkeypatch,
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
        workflow, "get_citation_passage_details",
        lambda target_record, paper, token: {
            "passages": ["The target is used as a baseline."],
            "target_citation_labels": ["[56]"],
            "target_citation_spans": [],
        },
    )
    monkeypatch.setattr(
        workflow, "summarize_paper",
        lambda target_record, record, passages, api_key: {
            "summary": "It provides a baseline.",
            "metadata": metadata,
        },
    )

    progress_messages = []
    result = workflow.summarize_citing_papers(
        "TARGET", token="ads-token", rows=1, api_key="openai-key",
        progress_callback=progress_messages.append,
    )

    assert result["citing_papers"] == [{
        "record": citing,
        "passages": ["The target is used as a baseline."],
        "target_citation_labels": ["[56]"],
        "target_citation_spans": [],
        "summary": "It provides a baseline.",
        "summary_metadata": metadata,
    }]
    assert progress_messages == [
        "Fetching target record TARGET from ADS...",
        "ADS found 17 citing papers; processing 1 (limit: 1).",
        "Processing citing paper 1/1: CITING",
        "[debug] Sending citation summary request to the LLM for CITING...",
    ]


def test_summarize_citing_papers_prints_progress_by_default(
    monkeypatch, capsys
):
    target = {
        "bibcode": "TARGET",
        "title": "Target paper",
        "author": ["Target, A."],
        "year": "2025",
    }
    citing = {"bibcode": "CITING", "title": "Citing paper", "year": "2026"}
    summarize = Mock()
    monkeypatch.setattr(workflow, "get_paper", lambda bibcode, token: target)
    monkeypatch.setattr(
        workflow, "get_citing_papers",
        lambda bibcode, token, rows: ([citing], 1),
    )
    monkeypatch.setattr(workflow, "normalise_record", lambda record: record)
    monkeypatch.setattr(
        workflow, "summarize_target_paper",
        lambda record, api_key: {"summary": "Target summary", "metadata": None},
    )
    monkeypatch.setattr(
        workflow, "get_citation_passage_details",
        lambda *args: {
            "passages": [],
            "target_citation_labels": [],
            "target_citation_spans": [],
        },
    )
    monkeypatch.setattr(workflow, "summarize_paper", summarize)

    result = workflow.summarize_citing_papers("TARGET")

    summarize.assert_not_called()
    assert capsys.readouterr().out.splitlines() == [
        "Fetching target record TARGET from ADS...",
        "ADS found 1 citing papers; processing 1 (limit: 10).",
        "Processing citing paper 1/1: CITING",
    ]
    assert result["citing_papers"] == [{
        "record": citing,
        "passages": [],
        "target_citation_labels": [],
        "target_citation_spans": [],
        "summary": (
            "No citation passages were available, so there is not enough "
            "context to determine how this paper uses Target (2025)."
        ),
        "summary_metadata": None,
    }]
