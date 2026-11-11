"""Render citation summaries as a standalone HTML report."""

from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import quote

from src.normalize import format_citation_label


_MATHML_ELEMENTS = {
    "math", "mrow", "mi", "mn", "mo", "ms", "mtext", "mspace",
    "msup", "msub", "msubsup", "mfrac", "msqrt", "mroot", "mstyle",
    "merror", "mpadded", "mphantom", "mfenced", "menclose", "mover",
    "munder", "munderover", "mtable", "mtr", "mtd", "semantics",
    "annotation",
}


class _TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.formula_depth = 0
        self.math_stack = []

    def handle_starttag(self, tag, attrs):
        name = tag.split(":")[-1]
        if name == "inline-formula":
            self.formula_depth += 1
        elif self.formula_depth and name in _MATHML_ELEMENTS:
            if name == "math":
                self.parts.append(
                    '<math xmlns="http://www.w3.org/1998/Math/MathML">'
                )
            else:
                self.parts.append(f"<{name}>")
            self.math_stack.append(name)
        elif not self.formula_depth:
            self.parts.append(escape(f"<{tag}>"))

    def handle_endtag(self, tag):
        name = tag.split(":")[-1]
        if name == "inline-formula":
            self.formula_depth -= 1
        elif self.formula_depth and self.math_stack and name == self.math_stack[-1]:
            self.math_stack.pop()
            self.parts.append(f"</{name}>")
        elif not self.formula_depth:
            self.parts.append(escape(f"</{tag}>"))

    def handle_data(self, data):
        self.parts.append(escape(data))


def _render_title(title):
    parser = _TitleParser()
    parser.feed(str(title or ""))
    return "".join(parser.parts)


def _render_passage(passage, target_citation_spans):
    parts = []
    position = 0
    for start, end in sorted(target_citation_spans or []):
        if start < position or end > len(passage):
            continue
        parts.append(escape(passage[position:start]))
        parts.append(
            '<mark class="target-citation">'
            f"{escape(passage[start:end])}</mark>"
        )
        position = end
    parts.append(escape(passage[position:]))
    return "".join(parts)


def _render_metadata(metadata):
    if not metadata:
        return ""

    created_at = metadata.get("created_at")
    created_at = (
        datetime.fromtimestamp(created_at, timezone.utc).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
        if created_at is not None else "unknown time"
    )
    return (
        '<details class="metadata"><summary>Generation details</summary>'
        '<small class="metadata">Generated with '
        f'{escape(str(metadata.get("model") or "unknown model"))}; '
        f'temperature {escape(str(metadata.get("temperature", "unknown")))}; '
        f'prompt {escape(str(metadata.get("prompt_version") or "unknown"))}; '
        f'response {escape(str(metadata.get("response_id") or "unknown"))}; '
        f'{escape(created_at)}</small></details>'
    )


def render_report(target_record, results, target_summary=None):
    """Return an HTML page for workflow results."""
    target_bibcode = escape(target_record.get("bibcode") or "", quote=True)
    target_title = _render_title(
        target_record.get("title") or "Untitled paper"
    )
    target_citation = escape(format_citation_label(target_record))
    target_url = escape(
        "https://ui.adsabs.harvard.edu/abs/" +
        quote(target_record.get("bibcode") or "", safe=""),
        quote=True,
    )
    target_summary = target_summary or {}
    target_summary_text = escape(
        target_summary.get("summary") or "No summary available."
    )
    target_summary_html = (
        '<article><h2>About this paper</h2>'
        f"<p>{target_summary_text}</p>"
        f'{_render_metadata(target_summary.get("metadata"))}</article>'
    )
    cards = []
    for result in results:
        record = result["record"]
        title = _render_title(record.get("title") or "Untitled paper")
        bibcode = escape(record.get("bibcode") or "")
        paper_url = escape(
            "https://ui.adsabs.harvard.edu/abs/" +
            quote(record.get("bibcode") or "", safe=""),
            quote=True,
        )
        year = escape(str(record.get("year") or "Year unknown"))
        summary = escape(result.get("summary") or "No summary available.")
        metadata_note = _render_metadata(result.get("summary_metadata"))
        target_citation_spans = result.get("target_citation_spans") or []
        passage_items = []
        for index, passage in enumerate(result["passages"]):
            spans = (
                target_citation_spans[index]
                if index < len(target_citation_spans) else []
            )
            passage_items.append(
                f"<li>{_render_passage(passage, spans)}</li>"
            )
        passages = "".join(passage_items) or "<li>No citation passages found.</li>"
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
        '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-mml-svg.js">'
        "</script>"
        "<style>body{font:16px system-ui;max-width:800px;margin:2rem auto;"
        "padding:0 1rem;color:#20242a;background:#f5f7fa}"
        "article{background:white;padding:1rem 1.25rem;margin:1rem 0;"
        "border-radius:10px;box-shadow:0 2px 10px #1b2a3a18}"
        "a{color:#1769aa;text-decoration:none}a:hover{text-decoration:underline}"
        "mark.target-citation{background:#fff1a8;padding:0 .12em;"
        "border-radius:2px}"
        "h2{margin:.2rem 0}.bibcode,small{color:#586575}"
        "small.metadata{display:block;margin-top:.5rem;font-size:.8rem}"
        "details{margin-top:1rem}li{margin:.5rem 0}</style></head><body>"
        f'<h1>Citation report: <a href="{target_url}" target="_blank" '
        f'rel="noopener">{target_title}</a> — {target_citation}</h1>'
        f'<p class="bibcode">Target bibcode: {target_bibcode}</p>' +
        target_summary_html +
        "".join(cards) +
        "</body></html>"
    )


def save_report(results):
    """Save workflow results as HTML and JSON; return both file paths."""
    filename = (
        "citation_report_"
        f"{quote(results['target']['bibcode'], safe='')}"
    )
    report_directory = Path.cwd() / "citation_reports"
    report_directory.mkdir(exist_ok=True)

    json_path = report_directory / f"{filename}.json"
    json_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    html_path = report_directory / f"{filename}.html"
    html_path.write_text(
        render_report(
            results["target"],
            results["citing_papers"],
            results["target_summary"],
        ),
        encoding="utf-8",
    )
    return html_path, json_path
