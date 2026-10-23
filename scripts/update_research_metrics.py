#!/usr/bin/env python3
"""Refresh an explicitly sourced OpenAlex author snapshot in README and JSON.

Use OPENALEX_AUTHOR_ID to pin a verified OpenAlex author if ORCID lookup is
ambiguous. OPENALEX_API_KEY is optional for this single weekly request.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ORCID = "0000-0003-2421-1382"
START = "<!-- OPENALEX_METRICS_START -->"
END = "<!-- OPENALEX_METRICS_END -->"


def fetch_json(url, params=None):
    if params:
        url += ("&" if "?" in url else "?") + urlencode(params)
    headers = {"Accept": "application/json", "User-Agent": "adeniyi-research-portfolio/1.0"}
    key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    with urlopen(Request(url, headers=headers), timeout=25) as response:
        return json.load(response)


def identify_author():
    pinned = os.environ.get("OPENALEX_AUTHOR_ID", "").strip()
    if pinned:
        if not re.fullmatch(r"A\d+", pinned):
            raise ValueError("OPENALEX_AUTHOR_ID must look like A1234567890")
        author = fetch_json(f"https://api.openalex.org/authors/{pinned}")
    else:
        data = fetch_json("https://api.openalex.org/authors", {"filter": f"orcid:{ORCID}", "per_page": 25})
        candidates = data.get("results", [])
        matches = [a for a in candidates if "adeniyi" in a.get("display_name", "").lower()]
        if len(matches) != 1:
            raise ValueError(
                f"ORCID lookup returned {len(matches)} matching Adeniyi author records. "
                "Check your record at openalex.org and set OPENALEX_AUTHOR_ID "
                "to the verified OpenAlex author ID. No metrics were changed."
            )
        author = matches[0]
    name = author.get("display_name", "")
    if "adeniyi" not in name.lower():
        raise ValueError(f"Unexpected OpenAlex author identity: {name!r}")
    author_orcid = (author.get("orcid") or "").rstrip("/").split("/")[-1]
    if author_orcid and author_orcid != ORCID:
        raise ValueError(f"OpenAlex record ORCID mismatch: {author_orcid}")
    return author


def main():
    # Fetch and validate everything before changing files.
    author = identify_author()
    stats = author.get("summary_stats") or {}
    values = {
        "works_count": author.get("works_count"),
        "cited_by_count": author.get("cited_by_count"),
        "h_index": stats.get("h_index"),
        "i10_index": stats.get("i10_index"),
    }
    if any(type(v) is not int or v < 0 for v in values.values()):
        raise ValueError(f"Missing or invalid OpenAlex metrics: {values}")
    author_id = (author.get("id") or "").rstrip("/")
    if not re.fullmatch(r"https://openalex\.org/A\d+", author_id):
        raise ValueError(f"Invalid OpenAlex author ID: {author_id!r}")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = (
        f"**OpenAlex research impact** · **{values['works_count']:,}** indexed works · "
        f"**{values['cited_by_count']:,}** citations · **h-index {values['h_index']}** · "
        f"**i10-index {values['i10_index']}**  \n"
        f"*Updated {timestamp} · [OpenAlex author record]({author_id}). "
        "Counts vary by database; [Google Scholar](https://scholar.google.com/citations?user=QDAoQt8AAAAJ) "
        "and [Scopus](https://www.scopus.com/authid/detail.uri?authorId=55388336000) "
        "provide their own metrics.*"
    )
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(START) > readme.index(END):
        raise ValueError("README.md must contain one correctly ordered OpenAlex metrics marker pair")
    updated = re.sub(re.escape(START) + r".*?" + re.escape(END),
                     lambda _: f"{START}\n{summary}\n{END}", readme, flags=re.S)
    snapshot = {"source": "OpenAlex", "retrieved_at_utc": timestamp, "author_name": author["display_name"],
                "author_id": author_id, "orcid": ORCID, **values}
    snapshot_path = ROOT / "data" / "research_metrics.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readme_path.write_text(updated, encoding="utf-8")
    print(f"Updated OpenAlex snapshot for {author['display_name']}: {values}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, HTTPError, URLError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"OpenAlex refresh failed; previously committed snapshot retained: {exc}", file=sys.stderr)
        sys.exit(1)
