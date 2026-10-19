"""Find in-text passages linked to a target paper's bibliography entry."""

from html.parser import HTMLParser


class _CitationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = {}
        self.paragraphs = []
        self.reference_id = None
        self.reference_tag = None
        self.reference_text = []
        self.paragraph = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id", "")
        if self.reference_id is None and element_id.startswith("bib."):
            self.reference_id = element_id
            self.reference_tag = tag
            self.reference_text = []
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
            self.references[self.reference_id] = " ".join(
                "".join(self.reference_text).split()
            )
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
    year = str(target_record.get("year") or "")

    target_references = {
        reference_id
        for reference_id, reference_text in parser.references.items()
        if any(value in reference_text.casefold() for value in identifiers)
        or (title and year and title.casefold() in reference_text.casefold()
            and year in reference_text)
    }
    if not target_references and year:
        authors = target_record.get("author") or []
        if authors:
            first_author = authors[0].split(",", 1)[0].strip().casefold()
            author_year_references = {
                reference_id
                for reference_id, reference_text in parser.references.items()
                if first_author in reference_text.casefold()
                and year in reference_text
            }
            if len(author_year_references) == 1:
                target_references = author_year_references

    return [
        " ".join("".join(paragraph["text"]).split())
        for paragraph in parser.paragraphs
        if any(ref in target_references for ref in paragraph["references"])
    ]
