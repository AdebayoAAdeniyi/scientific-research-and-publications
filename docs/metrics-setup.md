# Optional Google Scholar metrics automation

This workflow fetches **Google Scholar author metrics through SerpApi**, not through an official free Google Scholar API. SerpApi is a third-party service whose quota/prices can change.

1. Create a SerpApi account and obtain an API key after reviewing its pricing.
2. In your GitHub repository, choose **Settings → Secrets and variables → Actions → New repository secret**. Name it `SERPAPI_KEY` and paste your key (never commit it).
3. Under **Settings → Actions → General → Workflow permissions**, allow the workflow to write repository contents when your repository security settings permit it.
4. Push the supplied workflow to the default branch. Run it manually under **Actions → Update Google Scholar metrics → Run workflow** to confirm the response works.
5. The scheduled job runs weekly and updates the marked README section with citation count, h-index, i10-index and UTC retrieval time. The live Scholar profile link is always available.

If the API key is absent or the request fails, the workflow exits or fails without replacing valid metrics. Quotas, workflow scheduling and GitHub permission settings may affect regular updates. **Do not present the CV-reported historical h-index as a live figure.**

The metric values originate from Scholar as returned by the third-party service; discrepancies with Scopus or OpenAlex are expected because their indexing differs.
