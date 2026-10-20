"""Create an HTML report for papers citing an ADS record.

From the project root, set ADS_API_TOKEN and OPENAI_API_KEY, then run:
    python3.12 -m src.cli "TARGET_BIBCODE"
"""

import argparse
from pathlib import Path

from src.report import render_report
from src.workflow import summarize_citing_papers


def main():
    parser = argparse.ArgumentParser(
        description="Summarize papers citing an ADS record."
    )
    parser.add_argument("target_bibcode")
    parser.add_argument("--rows", type=int, default=10)
    args = parser.parse_args()

    print(f"Processing papers citing {args.target_bibcode}...", flush=True)
    results = summarize_citing_papers(args.target_bibcode, rows=args.rows)
    report_path = Path.cwd() / "citation_report.html"
    print("Rendering HTML report...", flush=True)
    report_path.write_text(render_report(results), encoding="utf-8")
    print(f"Saved HTML report to {report_path}")
    print("Open this file in a web browser to view it.")


if __name__ == "__main__":
    main()
