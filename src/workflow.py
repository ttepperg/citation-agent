"""Process citing papers into normalized records, passages, and summaries."""

from src.ads import get_paper, get_citing_papers
from src.normalize import format_citation_label, normalise_record
from src.passages import get_citation_passage_details
from src.summarize import summarize_paper, summarize_target_paper


def summarize_citing_papers(
    target_bibcode, token=None, rows=10, api_key=None, progress_callback=None
):
    """Return citing-paper results and send progress to a callback or stdout."""

    def report_progress(message):
        if progress_callback is None:
            print(message, flush=True)
        else:
            progress_callback(message)

    report_progress(f"Fetching target record {target_bibcode} from ADS...")
    target = get_paper(target_bibcode, token)
    if target is None:
        raise LookupError(f"ADS did not find {target_bibcode}")
    target_record = normalise_record(target)
    if target_record.get("abstract"):
        report_progress("[debug] Sending target summary request to the LLM...")
    target_summary = summarize_target_paper(target_record, api_key)

    citing_papers, total_citing_papers = get_citing_papers(
        target_bibcode, token, rows
    )
    report_progress(
        f"ADS found {total_citing_papers} citing papers; "
        f"processing {len(citing_papers)} (limit: {rows})."
    )
    results = []
    for index, paper in enumerate(citing_papers, 1):
        report_progress(
            f"Processing citing paper {index}/{len(citing_papers)}: "
            f"{paper['bibcode']}"
        )
        record = normalise_record(paper)
        passage_details = get_citation_passage_details(target, paper, token)
        passages = passage_details["passages"]
        if passages:
            report_progress(
                f"[debug] Sending citation summary request to the LLM for "
                f"{record['bibcode']}..."
            )
            summary_result = summarize_paper(
                target_record, record, passages, api_key
            )
        else:
            summary_result = {
                "summary": (
                    "No citation passages were available, so there is not "
                    "enough context to determine how this paper uses "
                    f"{format_citation_label(target_record)}."
                ),
                "metadata": None,
            }
        results.append({
            "record": record,
            "passages": passages,
            "target_citation_labels": passage_details[
                "target_citation_labels"
            ],
            "target_citation_spans": passage_details[
                "target_citation_spans"
            ],
            "summary": summary_result["summary"],
            "summary_metadata": summary_result["metadata"],
        })
    return {
        "target": target_record,
        "target_summary": target_summary,
        "citing_papers": results,
    }
