"""Summarize papers citing an ADS record.

From the project root, set ADS_API_TOKEN and OPENAI_API_KEY, then run:
    python3.12 -m src.cli "TARGET_BIBCODE"
"""

import argparse
import json

from src.workflow import summarize_citing_papers


def main():
    parser = argparse.ArgumentParser(
        description="Summarize papers citing an ADS record."
    )
    parser.add_argument("target_bibcode")
    parser.add_argument("--rows", type=int, default=10)
    args = parser.parse_args()

    results = summarize_citing_papers(args.target_bibcode, rows=args.rows)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
