"""Run a live check from ADS citation retrieval through summarization.

From the project root, set ADS_API_TOKEN and OPENAI_API_KEY, then run:
    python3.12 -m extras.check_summary "TARGET_BIBCODE" "CITING_BIBCODE"
"""

import sys

from extras.check_passages import check_known_citation
from src.ads import get_paper
from src.normalize import normalise_record
from src.summarize import summarize_paper


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python3.12 -m extras.check_summary "
            '"TARGET_BIBCODE" "CITING_BIBCODE"'
        )
    try:
        target_bibcode, citing_bibcode = sys.argv[1:]
        citing_paper = get_paper(citing_bibcode)
        if citing_paper is None:
            raise LookupError(f"ADS did not find {citing_bibcode}")

        citing_paper, passages = check_known_citation(
            target_bibcode, citing_paper
        )
        print(f"Extracted {len(passages)} citation passages.")
        print(summarize_paper(normalise_record(citing_paper), passages))
    except (RuntimeError, TimeoutError) as exc:
        raise SystemExit(str(exc)) from None
