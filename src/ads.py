"""Retrieve papers that cite an ADS record."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src.normalize import normalise_record


def _get_ads_data(request, action):
    for attempt in range(2):
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            raise RuntimeError(
                f"ADS returned HTTP {exc.code} while {action}."
            ) from exc
        except (TimeoutError, URLError) as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, TimeoutError) and attempt == 0:
                continue
            if isinstance(reason, TimeoutError):
                raise TimeoutError(
                    f"Timed out contacting ADS while {action}, after one retry."
                ) from exc
            raise RuntimeError(
                f"Network error contacting ADS while {action}: {reason}"
            ) from exc


def get_paper(bibcode, token=None):
    """Return the raw ADS record for bibcode, or None if it is not found."""
    token = token or os.environ.get("ADS_API_TOKEN")
    if not token:
        raise ValueError("Set ADS_API_TOKEN or pass an ADS API token.")

    params = urlencode({
        "q": f"bibcode:{bibcode}",
        "fl": "bibcode,title,author,year,doi,abstract",
        "rows": 1,
    })
    request = Request(
        f"https://api.adsabs.harvard.edu/v1/search/query?{params}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = _get_ads_data(request, f"fetching record {bibcode}")
    docs = data["response"]["docs"]
    return docs[0] if docs else None


def get_citing_papers(bibcode, token=None, rows=10):
    """Return citing records and total hits; set ADS_API_TOKEN or pass token."""
    token = token or os.environ.get("ADS_API_TOKEN")
    if not token:
        raise ValueError("Set ADS_API_TOKEN or pass an ADS API token.")

    params = urlencode({
        "q": f"citations(bibcode:{bibcode})",
        "fl": "bibcode,title,author,year,doi,abstract",
        "rows": rows,
    })
    request = Request(
        f"https://api.adsabs.harvard.edu/v1/search/query?{params}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = _get_ads_data(request, f"fetching papers citing {bibcode}")
    response = data["response"]
    return response["docs"], response["numFound"]


def get_citing_papers_normalised(bibcode, token=None, rows=10):
    """Return normalized records for papers citing bibcode."""
    records, _ = get_citing_papers(bibcode, token, rows)
    return [
        normalise_record(record)
        for record in records
    ]


def get_paper_and_citing_papers_normalised(bibcode, token=None, rows=10):
    """Return the normalized input record and its normalized citing records."""
    paper = get_paper(bibcode, token)
    return {
        "input_record": normalise_record(paper) if paper else None,
        "citing_records": get_citing_papers_normalised(bibcode, token, rows),
    }
