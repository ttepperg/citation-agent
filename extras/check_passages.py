"""Check citation passage matching on a real ADS paper."""

import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from src.ads import get_paper
from src.passages import find_citation_passages


def _get_url(url, service, read=False):
    for attempt in range(2):
        try:
            with urlopen(url, timeout=30) as response:
                return response.geturl(), response.read() if read else None
        except HTTPError as exc:
            raise RuntimeError(
                f"{service} returned HTTP {exc.code}."
            ) from exc
        except (TimeoutError, URLError) as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, TimeoutError) and attempt == 0:
                continue
            if isinstance(reason, TimeoutError):
                raise TimeoutError(
                    f"Timed out contacting {service}, after one retry."
                ) from exc
            raise RuntimeError(
                f"Network error contacting {service}: {reason}"
            ) from exc


def check_known_citation(target_bibcode, citing_paper):
    """Check a citing paper's arXiv HTML for citations to an ADS record."""
    print(f"Fetching target record {target_bibcode} from ADS...", flush=True)
    target = get_paper(target_bibcode)
    if target is None:
        raise LookupError(f"ADS did not find {target_bibcode}")

    citing_bibcode = citing_paper["bibcode"]
    print(f"Resolving arXiv HTML for {citing_bibcode} through ADS...", flush=True)
    resolver_url = (
        f"https://ui.adsabs.harvard.edu/link_gateway/"
        f"{citing_bibcode}/eprint_html"
    )
    resolved_url, _ = _get_url(resolver_url, "ADS link resolver")
    html_url = resolved_url.replace("arxiv.org/abs/", "arxiv.org/html/", 1)

    print(f"Fetching {html_url}...", flush=True)
    _, html = _get_url(html_url, "arXiv HTML download", read=True)
    html = html.decode("utf-8", errors="replace")

    print("Matching bibliography entry and in-text links...", flush=True)
    return citing_paper, find_citation_passages(html, target)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python -m extras.check_passages TARGET_BIBCODE CITING_BIBCODE"
        )
    try:
        target_bibcode, citing_bibcode = sys.argv[1:]
        citing_paper = get_paper(citing_bibcode)
        if citing_paper is None:
            raise LookupError(f"ADS did not find {citing_bibcode}")
        citing_paper, passages = check_known_citation(
            target_bibcode, citing_paper
        )
        print(
            f"Citing paper: {citing_paper['bibcode']} — "
            f"{citing_paper['title'][0]}"
        )
        print(f"Linked in-text passages: {len(passages)}")
        for passage in passages:
            print(f"- {passage}")
    except (RuntimeError, TimeoutError) as exc:
        raise SystemExit(str(exc)) from None
