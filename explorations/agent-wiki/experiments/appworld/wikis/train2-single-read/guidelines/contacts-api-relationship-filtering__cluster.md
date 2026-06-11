---
type: cluster
slug: contacts-api-relationship-filtering
title: Use contacts API for relationship-based filtering
tags: [contacts, relationships, filtering]
verified_at: 2026-06-10
members:
  - id: 16f6835b55ef
    link: filter-entities-using-contact__16f6835b55ef.md
  - id: 71262af0cdc7
    link: use-contacts-api-for-relationship__71262af0cdc7.md
priority: high
---

# Use contacts API for relationship-based filtering

Tasks often require identifying users based on relationships such as friends, coworkers, or siblings. These guidelines direct agents to use the contacts API and filter by the 'relationships' field, rather than making assumptions or hardcoding relationships. This approach ensures that relationship-based queries are accurate and up-to-date.

## Takeaway

Always use the contacts API with the appropriate relationship filter to identify users for relationship-based tasks. Do not assume or hardcode relationships; query the contact book for current information.

## Members

These guidelines are kept as separate pages for full provenance back to their source trajectories. The cluster references them; nothing is moved or merged.

### [Filter entities using contact relationships](filter-entities-using-contact__16f6835b55ef.md)

- **id:** `16f6835b55ef`
- **trigger:** When a task requires acting only on items related to friends, coworkers, or other relationship-based groups.
- **source:** [appworld__aw_r](../summaries/appworld__aw_react_train2_baseline__6ea6792_3.md)

> To identify users who are friends or coworkers, retrieve your contacts and filter by the 'relationships' field. Use this filtered set to match against entities (e.g., payment request senders) when a task refers to 'friends' or 'coworkers'.

### [Use contacts API for relationship queries](use-contacts-api-for-relationship__71262af0cdc7.md)

- **id:** `71262af0cdc7`
- **trigger:** When you need to find users with a particular relationship (e.g., sibling, parent) for a task.
- **source:** [appworld__aw_r](../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)

> To identify users with a specific relationship (such as siblings), use the phone app's contacts API with the appropriate relationship filter. Do not assume or hardcode relationships; always query the contact book for up-to-date information.
