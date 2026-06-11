---
id: ca7497056794
type: guideline
trigger: When you need to log in to any connected app and require a password or other credential.
agent: appworld-react-code
tags: [credentials, security, api-usage]
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json
related_summary: summaries/appworld__aw_react_train2_baseline__2a163ab_2.md
verified_at: 2026-06-10
cluster: supervisor-api-credentials__cluster.md
superseded_by: supervisor-api-credentials__cluster.md
---

# Always retrieve credentials via supervisor API

When authentication is required for an app, retrieve the relevant credentials (such as passwords) using the supervisor app's API rather than hardcoding or guessing values. This ensures you use up-to-date and valid credentials for each account.

## Rationale

Credentials may change over time and should not be assumed or stored statically. Using the supervisor API guarantees accuracy and security.

## Used by

_(no recalls yet)_

## Sources

- [trajectory summary](../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json)
