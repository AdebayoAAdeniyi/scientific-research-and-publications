# Research metrics: OpenAlex automation

The research-impact section in the repository `README.md` is updated weekly from **OpenAlex** using GitHub Actions. This reports **OpenAlex figures**, not Google Scholar or Scopus figures. Only one API author lookup is needed per run; basic OpenAlex access is free and can run without an API key. A free API key is optional if keyless requests are restricted.

## First-time setup

1. Upload `README.md`, `scripts/update_research_metrics.py`, `docs/metrics-setup.md`, and `.github/workflows/update-research-metrics.yml` from the replacement bundle, preserving paths. Delete the older `.github/workflows/update-scholar.yml` and `scripts/update_scholar_metrics.py` (no longer used).
2. Confirm the new workflow appears in your GitHub repository's **Actions** tab. If disabled, enable GitHub Actions.
3. Go to **Actions → Update research metrics (OpenAlex) → Run workflow**. The script queries OpenAlex for ORCID `0000-0003-2421-1382`; it checks that the author record is an Adeniyi record and that the numbers are present.
4. If the workflow succeeds, it updates `README.md` and adds `data/research_metrics.json`, committing them automatically. The workflow runs each Monday at 09:17 UTC (GitHub schedules can be delayed).
5. If a commit/push is denied, go to **Settings → Actions → General → Workflow permissions** and ensure Actions is allowed to write repository contents. The YAML already requests `contents: write`.

## If there are multiple OpenAlex profiles (important)

OpenAlex can have multiple author profiles for the same researcher; some older works can be assigned elsewhere. If the action reports ambiguous ORCID matches, **do not select the biggest author blindly**. Open your record on https://openalex.org, check its works and affiliations, then set **Settings → Secrets and variables → Actions → Variables → New repository variable**:

- `OPENALEX_AUTHOR_ID` = the confirmed ID such as `A1234567890` (this is an illustration, **not** your actual author ID).

Run the action again. If its publication count differs from the 71 journal articles in the repository, that may be a coverage/disambiguation issue; do not label the numbers as your hand-curated 71-paper bibliography.

## Optional free API key

For basic weekly queries, **no key is required** according to current OpenAlex API docs. To obtain a free key if necessary, go to https://openalex.org, register, and verify your email. Under **Settings → API key**, copy the key. Add it as a GitHub Actions repository secret named `OPENALEX_API_KEY` (never add keys to `.yml` or code). The script will automatically use it when present.

## Local verification (Ubuntu)

Run `python3 scripts/update_research_metrics.py` in the repository root. If you have already identified a unique OpenAlex profile, optionally use `OPENALEX_AUTHOR_ID=A... python3 scripts/update_research_metrics.py`. Inspect `git diff README.md` and `cat data/research_metrics.json` before committing any local output.

## Common problems

- **Author not found / ambiguous:** verify the ORCID and pin the correct author with `OPENALEX_AUTHOR_ID`.
- **401/403/429:** verify optional key or try again later; the previous published snapshot is not overwritten.
- **Push denied:** check Actions workflow permission to write repository contents.
- **No weekly updates:** GitHub schedules can be delayed, and activity-disabled repositories may stop scheduled workflows. Use **Run workflow** to test.
- **Different citation values:** OpenAlex, Scopus, and Google Scholar have different coverage and indexing. This is normal.

Sources: https://help.openalex.org/api/authentication/ ; https://help.openalex.org/data/authors/orcid/ ; https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
