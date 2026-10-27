"""Convert raw ADS records to a consistent paper record."""


def normalise_record(record):
    """Return the paper's identity and abstract in a consistent shape."""
    title = record.get("title")
    if isinstance(title, list):
        title = title[0] if title else None

    return {
        "bibcode": record.get("bibcode"),
        "title": title,
        "author": record.get("author") or [],
        "year": record.get("year"),
        "doi": record.get("doi") or [],
        "abstract": record.get("abstract"),
    }


def format_citation_label(record):
    """Return a consistent author–year label for a paper record."""
    authors = [
        author.split(",", 1)[0].strip()
        for author in record.get("author") or []
    ]
    if len(authors) > 2:
        citation_authors = f"{authors[0]} et al."
    elif len(authors) == 2:
        citation_authors = f"{authors[0]} & {authors[1]}"
    else:
        citation_authors = authors[0] if authors else "Unknown author"
    return f"{citation_authors} ({record.get('year') or 'year unknown'})"
