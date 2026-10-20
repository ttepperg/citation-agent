# Citation Agent

Retrieve and normalize ADS records for papers that cite a given ADS bibcode.

## Use

Set your ADS API token in the environment:

```sh
export ADS_API_TOKEN="your ADS API token"
```

Set your OpenAI API key as well to summarize citation passages:

```sh
export OPENAI_API_KEY="your OpenAI API key"
```

Run the pipeline from the project root with a target ADS bibcode:

```sh
python3.12 -m src.cli "1998AJ....116.1009R"
```

The command saves `citation_report.html` in the current directory and prints
its path. Open that file in a web browser to view each citing paper's
normalized record, extracted passages, and summary. Use `--rows` to change the
maximum number of citing papers retrieved (default: 10).

For example, request up to 20 citing papers with:

```sh
python3.12 -m src.cli "2024MNRAS.535..187T" --rows 20
```

From the project root, retrieve normalized records for a bibcode:

```sh
python3.12 -c 'from src.ads import get_citing_papers_normalised; print(get_citing_papers_normalised("1998AJ....116.1009R"))'
```

Each result contains `bibcode`, `title`, `author`, `year`, and `doi`. The default query returns up to 10 citing papers.

## One-paper live checks

These optional scripts check a known target and citing-paper pair. Set
`ADS_API_TOKEN` before either command. To extract citation passages only, run
from the project root:

```sh
python3.12 -m extras.check_passages "2016A&A...594A..13P" "2020A&A...641A...6P"
```

To also summarize the citation passages, set `OPENAI_API_KEY` and run:

```sh
python3.12 -m extras.check_summary "2016A&A...594A...13P" "2020A&A...641A...6P"
```

The main `src.cli` pipeline does not require either of these one-paper scripts.
