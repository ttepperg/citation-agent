# Citation Agent

Retrieve and normalize ADS records for papers that cite a given ADS bibcode.

## Use

Set your ADS API token in the environment:

```sh
export ADS_API_TOKEN="your ADS API token"
```

From the project root, retrieve normalized records for a bibcode:

```sh
python3.12 -c 'from src.ads import get_citing_papers_normalised; print(get_citing_papers_normalised("1998AJ....116.1009R"))'
```

Each result contains `bibcode`, `title`, `author`, `year`, and `doi`. The default query returns up to 10 citing papers.

## Live citation check

With `ADS_API_TOKEN` set, run the live check from the project root with a target bibcode and a citing-paper bibcode:

```sh
python3.12 -m extras.check_passages 2016A&A...594A..13P 2020A&A...641A...6P
```

The script retrieves both records from ADS, resolves the citing paper's arXiv HTML, and prints the in-text passages linked to the target paper.
