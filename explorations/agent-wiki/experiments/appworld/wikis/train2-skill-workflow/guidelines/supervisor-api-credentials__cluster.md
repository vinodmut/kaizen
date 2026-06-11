---
type: cluster
slug: supervisor-api-credentials
title: Always retrieve credentials via supervisor API
tags: [credentials, supervisor-api, authentication]
verified_at: 2026-06-10
members:
  - id: ca7497056794
    link: always-retrieve-credentials-via__ca7497056794.md
  - id: 03487fdd6432
    link: retrieve-credentials-via-supervisor-api__03487fdd6432.md
priority: high
---

# Always retrieve credentials via supervisor API

Many tasks require authentication to connected apps. Rather than hardcoding, guessing, or storing credentials insecurely, these guidelines emphasize always retrieving up-to-date credentials (such as passwords) using the supervisor app's credential retrieval API. This ensures both security and correctness, as credentials may change and must be fetched dynamically.

## Takeaway

Always obtain app credentials by calling the supervisor app's credential retrieval API, never by hardcoding or guessing values. This guarantees you use the correct, current credentials for authentication.

## Members

These guidelines are kept as separate pages for full provenance back to their source trajectories. The cluster references them; nothing is moved or merged.

### [Always retrieve credentials via supervisor API](always-retrieve-credentials-via__ca7497056794.md)

- **id:** `ca7497056794`
- **trigger:** When you need to log in to any connected app and require a password or other credential.
- **source:** [appworld__aw_r](../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)

> When authentication is required for an app, retrieve the relevant credentials (such as passwords) using the supervisor app's API rather than hardcoding or guessing values. This ensures you use up-to-date and valid credentials for each account.

### [Retrieve credentials via supervisor API](retrieve-credentials-via-supervisor-api__03487fdd6432.md)

- **id:** `03487fdd6432`
- **trigger:** When you need to log in to any app and require a password or other credential.
- **source:** [appworld__aw_r](../summaries/appworld__aw_react_train2_baseline__6ea6792_3.md)

> Always obtain app credentials such as passwords by calling the supervisor app's credential retrieval API (e.g., show_account_passwords) rather than hardcoding or guessing values. This ensures you use the correct, current credentials for authentication.
