"""Test OpenAI citation summarization using mocked API responses.

Run from the project root with:
    python3.12 -m pytest tests/test_summarize.py
"""

import io
import json
from unittest.mock import MagicMock

import pytest

from src import summarize


@pytest.mark.parametrize(
    ("authors", "citation_label"),
    [
        (["Davies, J."], "Davies (2026)"),
        (
            ["Davies, H.", "Tepper-Garcia, T."],
            "Davies & Tepper-Garcia (2026)",
        ),
        (
            ["Davies, H.", "Tepper-Garcia, T.", "McClure-Griffiths, N."],
            "Davies et al. (2026)",
        ),
    ],
)
def test_summarize_paper_sends_record_and_passages(
    monkeypatch, authors, citation_label
):
    result = {
        "id": "resp_test123",
        "model": "gpt-6-astra-2026-08-15",
        "created_at": 1790000000,
        "output": [{
            "type": "message",
            "content": [{"type": "output_text", "text": "  It provides a comparison.  "}],
        }],
    }
    open_url = MagicMock(return_value=io.BytesIO(json.dumps(result).encode()))
    monkeypatch.setattr(summarize, "urlopen", open_url)

    result = summarize.summarize_paper(
        {
            "bibcode": "2026MNRAS.547f2166D",
            "title": "Target paper",
            "author": authors,
            "year": "2026",
        },
        {"title": "Citing paper", "year": "2024"},
        ["The target provides the baseline.", "We extend its method."],
        api_key="test-key",
    )

    assert result == {
        "summary": "It provides a comparison.",
        "metadata": {
            "model": "gpt-6-astra-2026-08-15",
            "temperature": 1,
            "prompt_version": "citation-summary-v2",
            "response_id": "resp_test123",
            "created_at": 1790000000,
        },
    }
    request = open_url.call_args.args[0]
    payload = json.loads(request.data)
    assert request.full_url == "https://api.openai.com/v1/responses"
    assert request.get_header("Authorization") == "Bearer test-key"
    assert payload["model"] == "gpt-6-astra"
    assert payload["temperature"] == 1
    assert "Target paper" in payload["input"]
    assert authors[0] in payload["input"]
    assert f"Target citation label: {citation_label}" in payload["input"]
    assert (
        f"use exactly this citation label: {citation_label}"
        in payload["instructions"]
    )
    assert "2026MNRAS.547f2166D" in payload["input"]
    assert "Citing paper (2024)" in payload["input"]
    assert "The target provides the baseline." in payload["input"]
    assert "We extend its method." in payload["input"]
    open_url.assert_called_once_with(request, timeout=60)
