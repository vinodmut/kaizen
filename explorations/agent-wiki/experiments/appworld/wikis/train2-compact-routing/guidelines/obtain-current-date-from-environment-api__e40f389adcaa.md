---
id: e40f389adcaa
type: guideline
trigger: When you need to compute time ranges (e.g., 'yesterday') or respond to time-sensitive requests.
agent: appworld-react-code
tags: [datetime, environment, api-usage]
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json
related_summary: summaries/appworld__aw_react_train2_baseline__2a163ab_2.md
verified_at: 2026-06-10
---

# Obtain current date from environment API

Always obtain the current date and time from the environment or device API (such as get_current_date_and_time) rather than relying on your internal clock or assumptions.

## Rationale

The environment's current date and time may differ from your internal state. Using the API ensures consistency with the user's context.

## Used by

_(no recalls yet)_

## Sources

- [trajectory summary](../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json)
