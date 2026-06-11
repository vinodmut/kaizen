---
id: e56a8dc4874d
type: guideline
trigger: When you need to perform actions on a subset of data retrieved from an API, based on dynamic criteria.
agent: appworld-react-code
tags: [data-filtering, api-usage, runtime-logic]
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json
related_summary: summaries/appworld__aw_react_train2_baseline__2a163ab_2.md
verified_at: 2026-06-10
---

# Filter and act on API data using runtime logic

After retrieving data from APIs (such as social feeds or transactions), apply runtime filtering logic (e.g., by date or participant) before taking actions like liking or updating records. Do not assume the API provides all necessary filters.

## Rationale

APIs may not support all filtering options directly. Applying logic after data retrieval ensures you act only on relevant items.

## Used by

_(no recalls yet)_

## Sources

- [trajectory summary](../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json)
