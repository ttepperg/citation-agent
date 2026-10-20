"""Test HTML citation report rendering.

Run from the project root with:
    python3.12 -m pytest tests/test_report.py
"""

from src.report import render_report


def test_render_report_displays_and_escapes_citation_results():
    html = render_report([{
        "record": {
            "title": "Paper <one>",
            "year": "2024",
            "bibcode": "2024MNRAS.535..187T",
        },
        "passages": ["We extend <their> method."],
        "summary": "It provides a <baseline>.",
    }])

    assert "Paper &lt;one&gt;" in html
    assert "2024MNRAS.535..187T" in html
    assert "It provides a &lt;baseline&gt;." in html
    assert "We extend &lt;their&gt; method." in html
    assert "<details><summary>Citation passages</summary>" in html
