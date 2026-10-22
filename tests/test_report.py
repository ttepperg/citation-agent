"""Test HTML citation report rendering.

Run from the project root with:
    python3.12 -m pytest tests/test_report.py
"""

from src.report import render_report


def test_render_report_displays_and_escapes_citation_results():
    html = render_report(
        {
            "title": "Target <paper>",
            "bibcode": "1998AJ....116.1009R",
            "author": ["Target, A.", "Second, B.", "Third, C."],
            "year": "1998",
        },
        [{
            "record": {
                "title": "Paper <one>",
                "year": "2024",
                "bibcode": "2024MNRAS.535..187T",
            },
            "passages": ["We extend <their> method."],
            "summary": "It provides a <baseline>.",
            "summary_metadata": {
                "model": "gpt-6-astra <snapshot>",
                "temperature": 1,
                "prompt_version": "citation-summary-v2 <test>",
                "response_id": "resp_<id>",
                "created_at": 0,
            },
        }],
    )

    assert (
        'Citation report: <a href="https://ui.adsabs.harvard.edu/abs/'
        '1998AJ....116.1009R" target="_blank" rel="noopener">'
        'Target &lt;paper&gt;</a> — Target et al. (1998)'
    ) in html
    assert 'href="https://ui.adsabs.harvard.edu/abs/1998AJ....116.1009R"' in html
    assert "Paper &lt;one&gt;" in html
    assert 'href="https://ui.adsabs.harvard.edu/abs/2024MNRAS.535..187T"' in html
    assert 'target="_blank" rel="noopener">Paper &lt;one&gt;</a>' in html
    assert "2024MNRAS.535..187T" in html
    assert "It provides a &lt;baseline&gt;." in html
    assert "We extend &lt;their&gt; method." in html
    assert "<details><summary>Citation passages</summary>" in html
    assert "Generated with gpt-6-astra &lt;snapshot&gt;" in html
    assert "temperature 1" in html
    assert "prompt citation-summary-v2 &lt;test&gt;" in html
    assert "response resp_&lt;id&gt;" in html
    assert "1970-01-01 00:00 UTC" in html
