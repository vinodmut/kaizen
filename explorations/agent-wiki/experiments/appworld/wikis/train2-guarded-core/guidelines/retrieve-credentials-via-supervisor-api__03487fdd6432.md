---
id: 03487fdd6432
type: guideline
trigger: When you need to log in to any app and require a password or other credential.
agent: appworld-react-code
tags: [credentials, supervisor, security]
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json
related_summary: summaries/appworld__aw_react_train2_baseline__6ea6792_3.md
verified_at: 2026-06-10
cluster: supervisor-api-credentials__cluster.md
superseded_by: supervisor-api-credentials__cluster.md
---

# Retrieve credentials via supervisor API

Always obtain app credentials such as passwords by calling the supervisor app's credential retrieval API (e.g., show_account_passwords) rather than hardcoding or guessing values. This ensures you use the correct, current credentials for authentication.

## Rationale

Credentials may change over time and should not be assumed or stored statically. Retrieving them via the supervisor API guarantees accuracy and security, preventing authentication failures.

## Used by

_(no recalls yet)_

## Sources

- [trajectory summary](../summaries/appworld__aw_react_train2_baseline__6ea6792_3.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json)
