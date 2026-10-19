"""Test OpenAI citation summarization using mocked API responses.

Run from the project root with:
    python3.12 -m pytest tests/test_summarize.py
"""

import io
import json
from unittest.mock import MagicMock

from src import summarize


def test_summarize_paper_sends_record_and_passages(monkeypatch):
    result = {
        "output": [{
            "type": "message",
            "content": [{"type": "output_text", "text": "  It provides a comparison.  "}],
        }],
    }
    open_url = MagicMock(return_value=io.BytesIO(json.dumps(result).encode()))
    monkeypatch.setattr(summarize, "urlopen", open_url)

    summary = summarize.summarize_paper(
        {"title": "Citing paper", "year": "2024"},
        ["The target provides the baseline.", "We extend its method."],
        api_key="test-key",
    )

    assert summary == "It provides a comparison."
    request = open_url.call_args.args[0]
    payload = json.loads(request.data)
    assert request.full_url == "https://api.openai.com/v1/responses"
    assert request.get_header("Authorization") == "Bearer test-key"
    assert payload["model"] == "gpt-6-astra"
    assert "Citing paper (2024)" in payload["input"]
    assert "The target provides the baseline." in payload["input"]
    assert "We extend its method." in payload["input"]
    open_url.assert_called_once_with(request, timeout=60)
