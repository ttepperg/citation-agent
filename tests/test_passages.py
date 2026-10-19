"""Test citation passage extraction and unavailable arXiv HTML responses.

Run from the project root with:
    python3.12 -m pytest tests/test_passages.py
"""

from unittest.mock import MagicMock
from urllib.error import HTTPError

import pytest

from src import passages
from src.passages import find_citation_passages


def test_find_citation_passages_follows_links_to_target_reference():
    html = """
    <article>
      <p>First use links to <a href="#bib.bib1">Riess et al. (1998)</a>.</p>
      <p>Another discussion cites <a href="#bib.bib1">the same work</a>.</p>
      <p>Unrelated citation <a href="#bib.bib2">Other et al. (2001)</a>.</p>
      <ol>
        <li id="bib.bib1">Riess et al. Observational Evidence from Supernovae
          for an Accelerating Universe and a Cosmological Constant. 1998, AJ.
        </li>
        <li id="bib.bib2">Other et al. An unrelated paper. 2001.</li>
      </ol>
    </article>
    """
    target = {
        "bibcode": "1998AJ....116.1009R",
        "title": [
            "Observational Evidence from Supernovae for an Accelerating "
            "Universe and a Cosmological Constant"
        ],
        "year": "1998",
        "doi": [],
    }

    assert find_citation_passages(html, target) == [
        "First use links to Riess et al. (1998).",
        "Another discussion cites the same work.",
    ]


def test_find_citation_passages_matches_unique_author_year_reference():
    html = """
    <article>
      <p>We use the Nexus framework <a href="#bib.bib1">(2024)</a>.</p>
      <ol>
        <li id="bib.bib1">Tepper-García T., Bland-Hawthorn J., Vasiliev E.,
          Agertz O., Teyssier R., Federrath C., 2024, MNRAS</li>
        <li id="bib.bib2">Another author, 2023, MNRAS</li>
      </ol>
    </article>
    """
    target = {
        "bibcode": "2024MNRAS.535..187T",
        "title": ["Nexus: a framework for controlled simulations"],
        "author": ["Tepper-García, Thor"],
        "year": "2024",
        "doi": ["10.1093/mnras/stae2372"],
    }

    assert find_citation_passages(html, target) == [
        "We use the Nexus framework (2024)."
    ]


def test_find_citation_passages_ignores_ambiguous_author_year_references():
    html = """
    <article>
      <p>First work <a href="#bib.bib1">(2024a)</a>.</p>
      <p>Second work <a href="#bib.bib2">(2024b)</a>.</p>
      <ol>
        <li id="bib.bib1">Tepper-García T., First paper, 2024, MNRAS</li>
        <li id="bib.bib2">Tepper-García T., Second paper, 2024, MNRAS</li>
      </ol>
    </article>
    """
    target = {
        "bibcode": "2024MNRAS.535..187T",
        "title": ["Nexus: a framework for controlled simulations"],
        "author": ["Tepper-García, Thor"],
        "year": "2024",
        "doi": ["10.1093/mnras/stae2372"],
    }

    assert find_citation_passages(html, target) == []


@pytest.mark.parametrize("status", [403, 404])
def test_get_citation_passages_returns_empty_when_arxiv_html_unavailable(
    monkeypatch, status
):
    resolver_response = MagicMock()
    resolver_response.__enter__.return_value.read.return_value = (
        b'{"link": "https://arxiv.org/abs/1234.56789"}'
    )
    open_url = MagicMock(
        side_effect=[
            resolver_response,
            HTTPError(
                "https://arxiv.org/html/1234.56789",
                status,
                "Unavailable",
                {},
                None,
            ),
        ]
    )
    monkeypatch.setattr(passages, "urlopen", open_url)

    assert passages.get_citation_passages(
        {"bibcode": "target"}, {"bibcode": "citing"}, token="token"
    ) == []
