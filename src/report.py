"""Render citation summaries as a self-contained HTML report."""

from html import escape


def render_report(results):
    """Return an HTML page for workflow results."""
    cards = []
    for result in results:
        record = result["record"]
        title = escape(record.get("title") or "Untitled paper")
        bibcode = escape(record.get("bibcode") or "")
        year = escape(str(record.get("year") or "Year unknown"))
        summary = escape(result.get("summary") or "No summary available.")
        passages = "".join(
            f"<li>{escape(passage)}</li>" for passage in result["passages"]
        ) or "<li>No citation passages found.</li>"
        cards.append(
            f"<article><h2>{title} <small>({year})</small></h2>"
            f"<p class=\"bibcode\">{bibcode}</p>"
            f"<p>{summary}</p>"
            f"<details><summary>Citation passages</summary><ul>{passages}</ul>"
            "</details></article>"
        )

    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>Citation report</title>"
        "<style>body{font:16px system-ui;max-width:800px;margin:2rem auto;"
        "padding:0 1rem;color:#20242a;background:#f5f7fa}"
        "article{background:white;padding:1rem 1.25rem;margin:1rem 0;"
        "border-radius:10px;box-shadow:0 2px 10px #1b2a3a18}"
        "h2{margin:.2rem 0}.bibcode,small{color:#586575}"
        "details{margin-top:1rem}li{margin:.5rem 0}</style></head><body>"
        "<h1>Citation report</h1>"
        + "".join(cards)
        + "</body></html>"
    )
