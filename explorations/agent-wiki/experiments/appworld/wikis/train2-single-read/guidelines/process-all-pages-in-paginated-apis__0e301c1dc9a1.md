---
id: 0e301c1dc9a1
type: guideline
trigger: Whenever you need to retrieve a complete list of items from a paginated API endpoint.
agent: appworld-react-code
tags: [pagination, api-usage, data-completeness]
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json
related_summary: summaries/appworld__aw_react_train2_baseline__2a163ab_2.md
verified_at: 2026-06-10
cluster: iterate-all-pages-paginated-apis__cluster.md
superseded_by: iterate-all-pages-paginated-apis__cluster.md
---

# Process all pages in paginated APIs

When using paginated APIs, always iterate through all pages by incrementing the page_index until no more results are returned. Do not stop at the first page, as this may miss relevant data.

## Rationale

Paginated APIs only return a subset of results per page. Failing to process all pages can lead to incomplete task execution.

## Used by

_(no recalls yet)_

## Sources

- [trajectory summary](../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json)
