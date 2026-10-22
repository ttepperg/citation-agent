"""Render citation summaries as a self-contained HTML report."""

from datetime import datetime, timezone
from html import escape
from urllib.parse import quote

from src.normalize import format_citation_label


def render_report(target_record, results):
    """Return an HTML page for workflow results."""
    target_bibcode = escape(target_record.get("bibcode") or "", quote=True)
    target_title = escape(target_record.get("title") or "Untitled paper")
    target_citation = escape(format_citation_label(target_record))
    target_url = escape(
        "https://ui.adsabs.harvard.edu/abs/" +
        quote(target_record.get("bibcode") or "", safe=""),
        quote=True,
    )
    cards = []
    for result in results:
        record = result["record"]
        title = escape(record.get("title") or "Untitled paper")
        bibcode = escape(record.get("bibcode") or "")
        paper_url = escape(
            "https://ui.adsabs.harvard.edu/abs/" +
            quote(record.get("bibcode") or "", safe=""),
            quote=True,
        )
        year = escape(str(record.get("year") or "Year unknown"))
        summary = escape(result.get("summary") or "No summary available.")
        metadata = result.get("summary_metadata") or {}
        metadata_note = ""
        if metadata:
            created_at = metadata.get("created_at")
            created_at = (
                datetime.fromtimestamp(created_at, timezone.utc).strftime(
                    "%Y-%m-%d %H:%M UTC"
                )
                if created_at is not None else "unknown time"
            )
            metadata_note = (
                '<details class="metadata"><summary>Generation details</summary>'
                '<small class="metadata">Generated with '
                f'{escape(str(metadata.get("model") or "unknown model"))}; '
                f'temperature {escape(str(metadata.get("temperature", "unknown")))}; '
                f'prompt {escape(str(metadata.get("prompt_version") or "unknown"))}; '
                f'response {escape(str(metadata.get("response_id") or "unknown"))}; '
                f'{escape(created_at)}</small></details>'
            )
        passages = "".join(
            f"<li>{escape(passage)}</li>" for passage in result["passages"]
        ) or "<li>No citation passages found.</li>"
        cards.append(
            f'<article><h2><a href="{paper_url}" target="_blank" '
            f'rel="noopener">{title}</a> '
            f"<small>({year})</small></h2>"
            f"<p class=\"bibcode\">{bibcode}</p>"
            f"<p>{summary}</p>"
            f"<details><summary>Citation passages</summary><ul>{passages}</ul>"
            "</details>"
            f"{metadata_note}</article>"
        )

    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        f'<meta name="target-bibcode" content="{target_bibcode}">'
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>Citation report</title>"
        "<style>body{font:16px system-ui;max-width:800px;margin:2rem auto;"
        "padding:0 1rem;color:#20242a;background:#f5f7fa}"
        "article{background:white;padding:1rem 1.25rem;margin:1rem 0;"
        "border-radius:10px;box-shadow:0 2px 10px #1b2a3a18}"
        "a{color:#1769aa;text-decoration:none}a:hover{text-decoration:underline}"
        "h2{margin:.2rem 0}.bibcode,small{color:#586575}"
        "small.metadata{display:block;margin-top:.5rem;font-size:.8rem}"
        "details{margin-top:1rem}li{margin:.5rem 0}</style></head><body>"
        f'<h1>Citation report: <a href="{target_url}" target="_blank" '
        f'rel="noopener">{target_title}</a> — {target_citation}</h1>'
        f'<p class="bibcode">Target bibcode: {target_bibcode}</p>' +
        "".join(cards) +
        "</body></html>"
    )
