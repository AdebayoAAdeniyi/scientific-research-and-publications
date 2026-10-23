from pathlib import Path
import csv

root = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((root / "data/publications.csv").open(encoding="utf-8")))
assert len(rows) == 71, f"Expected 71 records, got {len(rows)}"
assert {int(r["number"]) for r in rows} == set(range(1, 72))
assert len([r for r in rows if r["doi"]]) == 70
assert len({r["doi"].lower() for r in rows if r["doi"]}) == 70
for row in rows:
    if row["doi"]:
        assert row["doi_url"] == "https://doi.org/" + row["doi"]
print("Catalogue structure OK: 71 records; 70 supplied DOIs; 1 missing DOI.")
