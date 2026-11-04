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

The command saves an HTML report and its JSON data to
`citation_reports/citation_report_<encoded-bibcode>.html` and
`citation_reports/citation_report_<encoded-bibcode>.json` in the current
working directory, creating `citation_reports/` if needed. It prints both
paths. Each target bibcode gets distinct filenames. The HTML report can be
opened in a browser; the JSON file contains the target, target summary, and
citing-paper records, passages, summaries, and generation metadata for use by
other tools. Use `--rows` to change the maximum number of citing papers
retrieved (default: 10).

## View a saved JSON report

Open `templates/citation_report.html` in a browser and select a JSON report
with the file picker. To load a report by bibcode instead, start a local server
from the project root:

```sh
python3.12 -m http.server --bind 127.0.0.1 8000
```

Then open this URL, replacing the bibcode as needed:

```text
http://127.0.0.1:8000/templates/citation_report.html?bibcode=2024MNRAS.535..187T
```

The viewer loads the matching JSON file from `citation_reports/`. In a bibcode
containing `&`, write `%26` in the URL.

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

## Acknowledgement

Built with Aeon ℵ (Codex)
