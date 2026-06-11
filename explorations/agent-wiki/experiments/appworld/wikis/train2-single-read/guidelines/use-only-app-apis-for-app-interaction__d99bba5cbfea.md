---
id: d99bba5cbfea
type: guideline
trigger: Whenever you need to perform actions within an app that exposes its own API surface.
agent: appworld-react-code
tags: [api, app-integration, compatibility]
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json
related_summary: summaries/appworld__aw_react_train2_baseline__6ea6792_3.md
verified_at: 2026-06-10
---

# Use only app APIs for app interaction

When interacting with an app, use only the provided app APIs rather than corresponding Python packages or OS-level modules. For example, use the venmo app API for Venmo operations, not third-party Python libraries.

## Rationale

System-level operations and unofficial packages may be restricted or unsupported in the environment. Using the official app APIs ensures compatibility and avoids permission errors.

## Used by

_(no recalls yet)_

## Sources

- [trajectory summary](../summaries/appworld__aw_react_train2_baseline__6ea6792_3.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json)
