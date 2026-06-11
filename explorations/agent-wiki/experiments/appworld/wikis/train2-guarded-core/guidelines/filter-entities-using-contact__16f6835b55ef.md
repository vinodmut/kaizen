---
id: 16f6835b55ef
type: guideline
trigger: When a task requires acting only on items related to friends, coworkers, or other relationship-based groups.
agent: appworld-react-code
tags: [contacts, filtering, relationships]
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json
related_summary: summaries/appworld__aw_react_train2_baseline__6ea6792_3.md
verified_at: 2026-06-10
cluster: contacts-api-relationship-filtering__cluster.md
superseded_by: contacts-api-relationship-filtering__cluster.md
---

# Filter entities using contact relationships

To identify users who are friends or coworkers, retrieve your contacts and filter by the 'relationships' field. Use this filtered set to match against entities (e.g., payment request senders) when a task refers to 'friends' or 'coworkers'.

## Rationale

Relying on explicit contact relationships ensures accurate identification of relevant people, avoiding errors from guessing or using incomplete criteria.

## Used by

_(no recalls yet)_

## Sources

- [trajectory summary](../summaries/appworld__aw_react_train2_baseline__6ea6792_3.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json)
