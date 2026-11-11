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


def test_render_report_preserves_unicode_math_and_escapes_markup():
    summary = "Accents: \u0129 and i\u0303; math: \\(A_2/A_0\\); markup: <tag> &."
    html = render_report(
        {"bibcode": "TARGET", "author": [], "year": "2024"},
        [{
            "record": {"bibcode": "CITING", "year": "2025"},
            "passages": [],
            "summary": summary,
        }],
    )

    assert "Accents: \u0129 and i\u0303; math: \\(A_2/A_0\\); " in html
    assert "markup: &lt;tag&gt; &amp;." in html


def test_render_report_converts_ads_mathml_title_to_safe_mathml():
    title = (
        "Hunting heavy decaying dark matter with Tibet "
        "<inline-formula><mml:math><mml:msub><mml:mrow>"
        "<mml:mi>AS</mml:mi></mml:mrow><mml:mi>γ</mml:mi>"
        "</mml:msub></mml:math></inline-formula> and LHAASO-KM2A"
    )

    html = render_report(
        {"bibcode": "TARGET", "title": title, "author": [], "year": "2026"},
        [],
    )

    assert "Tibet <math xmlns=\"http://www.w3.org/1998/Math/MathML\">" in html
    assert "<msub><mrow><mi>AS</mi></mrow><mi>γ</mi></msub></math>" in html
    assert "</inline-formula>" not in html


def test_render_report_highlights_target_citation_label():
    html = render_report(
        {"bibcode": "TARGET", "author": ["Target, A."], "year": "2025"},
        [{
            "record": {"bibcode": "CITING"},
            "passages": ["Previous simulations [56] and [57] show this."],
            "target_citation_labels": ["[56]"],
            "target_citation_spans": [[[21, 25]]],
            "summary": "It compares the simulations.",
        }],
    )

    assert (
        "Previous simulations <mark class=\"target-citation\">[56]</mark> "
        "and [57] show this."
    ) in html


def test_render_report_does_not_highlight_matching_digits_in_math():
    passage = r"\(\sigma_{\log_{10}J}\) (see Refs. [27, 1])"
    target_index = passage.rindex("1")
    html = render_report(
        {"bibcode": "TARGET", "author": [], "year": "2025"},
        [{
            "record": {"bibcode": "CITING"},
            "passages": [passage],
            "target_citation_spans": [[[target_index, target_index + 1]]],
            "summary": "It cites the target.",
        }],
    )

    assert r"\log_{10}J" in html
    assert "Refs. [27, <mark class=\"target-citation\">1</mark>]" in html
    assert html.count('<mark class="target-citation">') == 1
