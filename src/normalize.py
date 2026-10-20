"""Convert raw ADS records to a consistent paper record."""


def normalise_record(record):
    """Return bibcode, title, author, year, and doi in a consistent shape."""
    title = record.get("title")
    if isinstance(title, list):
        title = title[0] if title else None

    return {
        "bibcode": record.get("bibcode"),
        "title": title,
        "author": record.get("author") or [],
        "year": record.get("year"),
        "doi": record.get("doi") or [],
    }
