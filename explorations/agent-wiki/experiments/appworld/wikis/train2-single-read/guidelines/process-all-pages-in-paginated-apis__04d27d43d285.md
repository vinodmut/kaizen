---
id: 04d27d43d285
type: guideline
trigger: Whenever you call an API that supports pagination (e.g., show_received_payment_requests, search_contacts).
agent: appworld-react-code
tags: [pagination, api, data-integrity]
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json
related_summary: summaries/appworld__aw_react_train2_baseline__6ea6792_3.md
verified_at: 2026-06-10
cluster: iterate-all-pages-paginated-apis__cluster.md
superseded_by: iterate-all-pages-paginated-apis__cluster.md
---

# Process all pages in paginated APIs

When retrieving results from a paginated API, always loop through all pages using the page_index and page_limit parameters until no more results are returned. Aggregate results across all pages to ensure completeness.

## Rationale

Paginated APIs only return a subset of results per call. Failing to iterate through all pages can lead to incomplete data processing and missed items.

## Used by

_(no recalls yet)_

## Sources

- [trajectory summary](../summaries/appworld__aw_react_train2_baseline__6ea6792_3.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json)
