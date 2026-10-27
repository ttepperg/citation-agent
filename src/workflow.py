"""Process citing papers into normalized records, passages, and summaries."""

from src.ads import get_paper, get_citing_papers
from src.normalize import normalise_record
from src.passages import get_citation_passages
from src.summarize import summarize_paper, summarize_target_paper


def summarize_citing_papers(target_bibcode, token=None, rows=10, api_key=None):
    """Return the normalized target and its citing-paper results."""
    target = get_paper(target_bibcode, token)
    if target is None:
        raise LookupError(f"ADS did not find {target_bibcode}")
    target_record = normalise_record(target)
    target_summary = summarize_target_paper(target_record, api_key)

    citing_papers = get_citing_papers(target_bibcode, token, rows)
    print(f"Number of citing papers found: {len(citing_papers)}", flush=True)
    results = []
    for index, paper in enumerate(citing_papers, 1):
        print(
            f"Processing citing paper {index}/{len(citing_papers)}: "
            f"{paper['bibcode']}",
            flush=True,
        )
        record = normalise_record(paper)
        passages = get_citation_passages(target, paper, token)
        summary_result = summarize_paper(
            target_record, record, passages, api_key
        )
        results.append({
            "record": record,
            "passages": passages,
            "summary": summary_result["summary"],
            "summary_metadata": summary_result["metadata"],
        })
    return {
        "target": target_record,
        "target_summary": target_summary,
        "citing_papers": results,
    }
