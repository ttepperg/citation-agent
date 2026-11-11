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
        self.citation_anchor = None
        self.in_math = False

    def handle_starttag(self, tag, attrs):
        if self.in_math:
            return
        attrs = dict(attrs)
        element_id = attrs.get("id", "")
        if self.reference_id is not None and tag == "a":
            self.reference_links.append(attrs.get("href", ""))
        elif tag == "math" and self.paragraph is not None:
            tex = attrs.get("alttext")
            if tex:
                left, right = (
                    (r"\[", r"\]")
                    if attrs.get("display") == "block"
                    else (r"\(", r"\)")
                )
                self.paragraph["text"].append(f"{left}{tex}{right}")
                self.in_math = True
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
                self.citation_anchor = {
                    "id": href[1:],
                    "text": [],
                    "start": sum(map(len, self.paragraph["text"])),
                }
                self.paragraph["references"].append(self.citation_anchor)

    def handle_data(self, data):
        if self.in_math:
            return
        if self.reference_id is not None:
            self.reference_text.append(data)
        if self.paragraph is not None:
            self.paragraph["text"].append(data)
            if self.citation_anchor is not None:
                self.citation_anchor["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "math" and self.in_math:
            self.in_math = False
        elif tag == "a" and self.citation_anchor is not None:
            self.citation_anchor = None
        elif self.reference_id is not None and tag == self.reference_tag:
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
    return find_citation_passage_details(html, target_record)["passages"]


def find_citation_passage_details(html, target_record):
    """Return passages and the exact text of links to the target reference."""
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

    passages = []
    target_citation_labels = []
    target_citation_spans = []
    for paragraph in parser.paragraphs:
        matches = [
            reference for reference in paragraph["references"]
            if reference["id"] in target_references
        ]
        if not matches:
            continue
        raw_text = "".join(paragraph["text"])
        passages.append(" ".join(raw_text.split()))
        passage_spans = []
        for match in matches:
            label = " ".join("".join(match["text"]).split())
            if label and label not in target_citation_labels:
                target_citation_labels.append(label)
            if label:
                prefix = raw_text[:match["start"]]
                start = len(" ".join(prefix.split()))
                if prefix and prefix[-1].isspace():
                    start += 1
                passage_spans.append([start, start + len(label)])
        target_citation_spans.append(passage_spans)
    return {
        "passages": passages,
        "target_citation_labels": target_citation_labels,
        "target_citation_spans": target_citation_spans,
    }


def _normalise_title(title):
    return " ".join(
        "".join(
            " " if category(character).startswith("P") or character == "−"
            else character
            for character in title.casefold()
        ).split()
    )


def get_citation_passages(target_record, citing_paper, token=None):
    """Fetch and return passage text citing the target."""
    return get_citation_passage_details(
        target_record, citing_paper, token
    )["passages"]


def get_citation_passage_details(target_record, citing_paper, token=None):
    """Fetch passages and target citation labels from a citing paper."""
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
        return {
            "passages": [],
            "target_citation_labels": [],
            "target_citation_spans": [],
        }
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
        return {
            "passages": [],
            "target_citation_labels": [],
            "target_citation_spans": [],
        }
    return find_citation_passage_details(
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
