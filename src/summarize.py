"""Summarize how a cited paper is used in a citing paper."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.normalize import format_citation_label


MODEL = "gpt-6-astra"
TEMPERATURE = 1
PROMPT_VERSION = "citation-summary-v2"
TARGET_PROMPT_VERSION = "target-summary-v1"


def _generate_summary(instructions, input_text, prompt_version, api_key):
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Set OPENAI_API_KEY or pass an API key.")

    request_data = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "instructions": instructions,
        "input": input_text,
    }
    request = Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(request_data).encode("utf-8"),
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

    summary = "".join(
        part["text"]
        for item in result["output"] if item.get("type") == "message"
        for part in item["content"] if part.get("type") == "output_text"
    ).strip()
    return {
        "summary": summary,
        "metadata": {
            "model": result.get("model", MODEL),
            "temperature": TEMPERATURE,
            "prompt_version": prompt_version,
            "response_id": result.get("id"),
            "created_at": result.get("created_at"),
        },
    }


def summarize_paper(target, record, passages, api_key=None):
    """Return a summary and compact metadata for the model response."""
    target_authors = target.get("author") or []
    target_author = target_authors[0] if target_authors else "Unknown author"
    target_citation = format_citation_label(target)
    target_paper = (
        f"{target.get('title') or 'Unknown title'} by {target_author} "
        f"({target.get('year') or 'year unknown'}; "
        f"bibcode {target.get('bibcode') or 'unknown'})"
    )
    paper = f"{record.get('title') or 'Unknown title'} ({record.get('year') or 'year unknown'})"
    input_text = (
        f"Target paper: {target_paper}\n"
        f"Target citation label: {target_citation}\n"
        f"Citing paper: {paper}\n"
        "Citation passages:\n"
        + "\n".join(f"- {passage}" for passage in passages)
    )
    instructions = (
        "Summarize in one or two concise sentences how the identified "
        f"target paper is used in the citation passages. When naming it, "
        f'use exactly this citation label: {target_citation}. Do not use '
        "another author/year form or call it 'the target paper'; pronouns "
        "are fine after the first mention. Use only evidence in the "
        "passages; say if they do not provide enough context to determine "
        "the paper's specific use."
    )
    return _generate_summary(instructions, input_text, PROMPT_VERSION, api_key)


def summarize_target_paper(record, api_key=None):
    """Summarize a paper from its ADS title and abstract."""
    abstract = record.get("abstract")
    if not abstract:
        return {"summary": "No abstract available.", "metadata": None}

    input_text = (
        f"Title: {record.get('title') or 'Unknown title'}\n"
        f"Abstract:\n{abstract}"
    )
    instructions = (
        "Summarize the paper's purpose, approach, and main findings in two "
        "or three concise sentences. Use only information supported by the "
        "title and abstract."
    )
    return _generate_summary(
        instructions, input_text, TARGET_PROMPT_VERSION, api_key
    )
