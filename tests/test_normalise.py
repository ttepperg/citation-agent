"""Test normalization of ADS records.

Run from the project root with:
    python3.12 -m pytest tests/test_normalise.py
"""

from src.normalise import normalise_record


def test_normalise_record_maps_ads_fields():
    record = {
        "bibcode": "2020A&A...641A...6P",
        "title": ["Planck 2018 results. VI. Cosmological parameters"],
        "author": ["Planck Collaboration"],
        "year": "2020",
        "doi": ["10.1051/0004-6361/201833910"],
    }

    assert normalise_record(record) == {
        "bibcode": "2020A&A...641A...6P",
        "title": "Planck 2018 results. VI. Cosmological parameters",
        "author": ["Planck Collaboration"],
        "year": "2020",
        "doi": ["10.1051/0004-6361/201833910"],
    }


def test_normalise_record_defaults_missing_fields():
    assert normalise_record({}) == {
        "bibcode": None,
        "title": None,
        "author": [],
        "year": None,
        "doi": [],
    }
