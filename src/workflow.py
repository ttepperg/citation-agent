"""Process citing papers into normalized records, passages, and summaries."""

from src.ads import get_paper, get_citing_papers
from src.normalize import normalise_record
from src.passages import get_citation_passages
from src.summarize import summarize_paper


def summarize_citing_papers(target_bibcode, token=None, rows=10, api_key=None):
    """Return each citing paper's normalized record, passages, and summary."""
    target = get_paper(target_bibcode, token)
    if target is None:
        raise LookupError(f"ADS did not find {target_bibcode}")

    results = []
    for paper in get_citing_papers(target_bibcode, token, rows):
        record = normalise_record(paper)
        passages = get_citation_passages(target, paper, token)
        results.append({
            "record": record,
            "passages": passages,
            "summary": summarize_paper(record, passages, api_key),
        })
    return results
