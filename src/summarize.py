"""Summarize how a cited paper is used in a citing paper."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def summarize_paper(record, passages, api_key=None):
    """Return a concise summary of the target paper's use in citation passages."""
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Set OPENAI_API_KEY or pass an API key.")

    paper = f"{record.get('title') or 'Unknown title'} ({record.get('year') or 'year unknown'})"
    input_text = (
        f"Citing paper: {paper}\n"
        "Citation passages:\n"
        + "\n".join(f"- {passage}" for passage in passages)
    )
    request = Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps({
            "model": "gpt-6-astra",
            "instructions": (
                "Summarize in one or two concise sentences how the target paper "
                "is used in the citation passages. Use only evidence in the "
                "passages; say if they do not provide enough context."
            ),
            "input": input_text,
        }).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(
            f"OpenAI API returned HTTP {exc.code}: {exc.reason}"
        ) from exc
    except TimeoutError as exc:
        raise TimeoutError("Timed out contacting the OpenAI API.") from exc
    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, TimeoutError):
            raise TimeoutError("Timed out contacting the OpenAI API.") from exc
        raise RuntimeError(f"Network error contacting the OpenAI API: {reason}") from exc

    return "".join(
        part["text"]
        for item in result["output"] if item.get("type") == "message"
        for part in item["content"] if part.get("type") == "output_text"
    ).strip()
