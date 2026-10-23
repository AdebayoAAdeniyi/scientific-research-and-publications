"""Optional Google Scholar metrics update via third-party SerpApi service.

Requires SERPAPI_KEY environment variable. Does not scrape Google Scholar.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import urllib.parse
import urllib.request

root = Path(__file__).resolve().parents[1]
key = os.environ.get("SERPAPI_KEY")
if not key:
    print("SERPAPI_KEY not configured: keeping existing README metrics.")
    raise SystemExit(0)

params = urllib.parse.urlencode({
    "engine": "google_scholar_author", "author_id": "QDAoQt8AAAAJ",
    "api_key": key, "hl": "en"
})
req = urllib.request.Request("https://serpapi.com/search.json?" + params,
                             headers={"User-Agent": "research-portfolio-metrics/1.0"})
with urllib.request.urlopen(req, timeout=45) as resp:
    data = json.load(resp)
if data.get("error"):
    raise RuntimeError("SerpApi returned an error; no metrics written")
table = data.get("cited_by", {}).get("table", [])
values = {}
for entry in table:
    for metric in ("citations", "h_index", "i10_index"):
        if metric in entry:
            values[metric] = entry[metric]["all"]
if any(k not in values or not isinstance(values[k], int) for k in ("citations", "h_index", "i10_index")):
    raise ValueError("Unrecognized or incomplete Google Scholar metric response; no changes made")
when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
block = (f"**Google Scholar metrics** (retrieved {when} via SerpApi): "
         f"**{values['citations']:,} citations · h-index {values['h_index']} · "
         f"i10-index {values['i10_index']}**. "
         "[View live profile](https://scholar.google.com/citations?user=QDAoQt8AAAAJ).")
readme = root / "README.md"
content = readme.read_text(encoding="utf-8")
start, end = "<!-- SCHOLAR_METRICS_START -->", "<!-- SCHOLAR_METRICS_END -->"
a, b = content.split(start, 1)
_, c = b.split(end, 1)
readme.write_text(a + start + "\n" + block + "\n" + end + c, encoding="utf-8")
print(block)
