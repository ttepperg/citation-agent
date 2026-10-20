"""Find in-text passages linked to a target paper's bibliography entry."""

import json
import os
from html.parser import HTMLParser
from unicodedata import category
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class _CitationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = {}
        self.paragraphs = []
        self.reference_id = None
        self.reference_tag = None
        self.reference_text = []
        self.reference_links = []
        self.paragraph = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id", "")
        if self.reference_id is not None and tag == "a":
            self.reference_links.append(attrs.get("href", ""))
        elif self.reference_id is None and element_id.startswith("bib.bib"):
            self.reference_id = element_id
            self.reference_tag = tag
            self.reference_text = []
            self.reference_links = []
        elif self.reference_id is None and tag == "p" and self.paragraph is None:
            self.paragraph = {"text": [], "references": []}
        elif self.paragraph is not None and tag == "a":
            href = attrs.get("href", "")
            if href.startswith("#bib."):
                self.paragraph["references"].append(href[1:])

    def handle_data(self, data):
        if self.reference_id is not None:
            self.reference_text.append(data)
        if self.paragraph is not None:
            self.paragraph["text"].append(data)

    def handle_endtag(self, tag):
        if self.reference_id is not None and tag == self.reference_tag:
            self.references[self.reference_id] = {
                "text": " ".join("".join(self.reference_text).split()),
                "links": self.reference_links,
            }
            self.reference_id = None
            self.reference_tag = None
        elif tag == "p" and self.paragraph is not None:
            self.paragraphs.append(self.paragraph)
            self.paragraph = None


def find_citation_passages(html, target_record):
    """Return paragraphs linking to the bibliography entry for target_record."""
    parser = _CitationParser()
    parser.feed(html)

    identifiers = [target_record.get("bibcode")]
    identifiers.extend(target_record.get("doi") or [])
    identifiers = [value.casefold() for value in identifiers if value]
    titles = target_record.get("title") or []
    title = titles[0] if isinstance(titles, list) else titles
    title = _normalise_title(title) if title else ""
    year = str(target_record.get("year") or "")

    target_references = {
        reference_id
        for reference_id, reference in parser.references.items()
        if any(
            value in reference["text"].casefold()
            or any(value in link.casefold() for link in reference["links"])
            for value in identifiers
        )
    }
    if not target_references and title:
        title_references = {
            reference_id
            for reference_id, reference in parser.references.items()
            if title in _normalise_title(reference["text"])
        }
        if len(title_references) == 1:
            target_references = title_references
    if not target_references and year:
        authors = target_record.get("author") or []
        if authors:
            first_author = authors[0].split(",", 1)[0].strip().casefold()
            author_year_references = {
                reference_id
                for reference_id, reference in parser.references.items()
                if first_author in reference["text"].casefold()
                and year in reference["text"]
            }
            if len(author_year_references) == 1:
                target_references = author_year_references

    return [
        " ".join("".join(paragraph["text"]).split())
        for paragraph in parser.paragraphs
        if any(ref in target_references for ref in paragraph["references"])
    ]


def _normalise_title(title):
    return " ".join(
        "".join(
            " " if category(character).startswith("P") or character == "−"
            else character
            for character in title.casefold()
        ).split()
    )


def get_citation_passages(target_record, citing_paper, token=None):
    """Fetch a citing paper's arXiv HTML and return passages citing target."""
    citing_bibcode = citing_paper["bibcode"]
    token = token or os.environ.get("ADS_API_TOKEN")
    if not token:
        raise ValueError("Set ADS_API_TOKEN or pass an ADS API token.")
    resolver_request = Request(
        f"https://api.adsabs.harvard.edu/v1/resolver/"
        f"{citing_bibcode}/eprint_html",
        headers={"Authorization": f"Bearer {token}"},
    )
    _, resolver_data = _get_url(
        resolver_request, "ADS link resolver", read=True, allow_404=True
    )
    if resolver_data is None:
        return []
    resolved_url = json.loads(resolver_data)["link"]
    html_url = resolved_url.replace("arxiv.org/abs/", "arxiv.org/html/", 1)
    _, html = _get_url(
        Request(html_url, headers={"User-Agent": "citation-agent/0.1"}),
        "arXiv HTML download",
        read=True,
        allow_404=True,
        allow_403=True,
    )
    if html is None:
        return []
    return find_citation_passages(
        html.decode("utf-8", errors="replace"), target_record
    )


def _get_url(url, service, read=False, allow_404=False, allow_403=False):
    for attempt in range(2):
        try:
            with urlopen(url, timeout=30) as response:
                return response.geturl(), response.read() if read else None
        except HTTPError as exc:
            if (allow_404 and exc.code == 404) or (
                allow_403 and exc.code == 403
            ):
                return None, None
            raise RuntimeError(f"{service} returned HTTP {exc.code}.") from exc
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
