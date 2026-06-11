---
id: 71262af0cdc7
type: guideline
trigger: When you need to find users with a particular relationship (e.g., sibling, parent) for a task.
agent: appworld-react-code
tags: [contacts, relationships, api-usage]
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json
related_summary: summaries/appworld__aw_react_train2_baseline__2a163ab_2.md
verified_at: 2026-06-10
cluster: contacts-api-relationship-filtering__cluster.md
superseded_by: contacts-api-relationship-filtering__cluster.md
---

# Use contacts API for relationship queries

To identify users with a specific relationship (such as siblings), use the phone app's contacts API with the appropriate relationship filter. Do not assume or hardcode relationships; always query the contact book for up-to-date information.

## Rationale

Contact relationships may change, and the contact book is the authoritative source. Filtering by relationship ensures accuracy and adaptability.

## Used by

_(no recalls yet)_

## Sources

- [trajectory summary](../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json)
