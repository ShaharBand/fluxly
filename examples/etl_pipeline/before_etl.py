"""The one-off script from the article's "Before" section, for comparison."""

import argparse
import json
from pathlib import Path

import requests


def extract(source_url: str) -> list[dict[str, object]]:
    source_path = Path(source_url)
    if source_path.is_file():
        return json.loads(source_path.read_text(encoding="utf-8"))

    response = requests.get(source_url)
    return response.json()


def transform(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    clean = []
    for row in rows:
        clean.append(
            {
                "id": row["userId"],
                "email": row["email"].strip().lower(),
            }
        )
    return clean


def load(rows: list[dict[str, object]], dry_run: bool) -> None:
    if dry_run:
        print(f"Would load {len(rows)} rows")
        return
    print(f"Loaded {len(rows)} rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        raw = extract(args.source_url)
        clean = transform(raw)
        load(clean, args.dry_run)
    except Exception as error:
        print(f"Something failed: {error}")
