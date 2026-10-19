"""Test ADS record retrieval and normalization.

Run from the project root with:
    python3.12 -m pytest tests/test_ads.py
"""

import json
from io import BytesIO

from src import ads


def test_get_citing_papers_normalised(monkeypatch):
    monkeypatch.setattr(
        ads,
        "get_citing_papers",
        lambda bibcode, token=None, rows=10: [
            {
                "bibcode": "2020A&A...641A...6P",
                "title": ["Planck 2018 results"],
                "author": ["Planck Collaboration"],
                "year": "2020",
                "doi": ["10.1051/0004-6361/201833910"],
            }
        ],
    )

    assert ads.get_citing_papers_normalised("target") == [
        {
            "bibcode": "2020A&A...641A...6P",
            "title": "Planck 2018 results",
            "author": ["Planck Collaboration"],
            "year": "2020",
            "doi": ["10.1051/0004-6361/201833910"],
        }
    ]


def test_get_paper_returns_matching_record(monkeypatch):
    record = {"bibcode": "2020A&A...641A...6P", "title": ["Planck 2018 results"]}
    monkeypatch.setattr(
        ads,
        "urlopen",
        lambda request, timeout: BytesIO(
            json.dumps({"response": {"docs": [record]}}).encode()
        ),
    )

    assert ads.get_paper("2020A&A...641A...6P", token="test") == record


def test_get_paper_returns_none_when_not_found(monkeypatch):
    monkeypatch.setattr(
        ads,
        "urlopen",
        lambda request, timeout: BytesIO(b'{"response": {"docs": []}}'),
    )

    assert ads.get_paper("unknown", token="test") is None


def test_get_paper_and_citing_papers_normalised(monkeypatch):
    monkeypatch.setattr(
        ads,
        "get_paper",
        lambda bibcode, token=None: {
            "bibcode": "target",
            "title": ["Input paper"],
        },
    )
    monkeypatch.setattr(
        ads,
        "get_citing_papers_normalised",
        lambda bibcode, token=None, rows=10: [{"bibcode": "citing"}],
    )

    assert ads.get_paper_and_citing_papers_normalised("target") == {
        "input_record": {
            "bibcode": "target",
            "title": "Input paper",
            "author": [],
            "year": None,
            "doi": [],
        },
        "citing_records": [{"bibcode": "citing"}],
    }
