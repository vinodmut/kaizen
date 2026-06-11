# AGENTS.md - AppWorld compact routing

This wiki is AppWorld train-set memory. Treat it as prior experience, not
ground truth. The current task prompt, current API docs, and current API outputs
are authoritative.

## Read Budget

Read this file once after seeing the actual task request. In this small wiki,
do not read `_index.jsonl` unless this file is unclear.

This wiki currently covers only Venmo tasks that use phone contacts. If the
current task is for Spotify, Gmail, Todoist, Amazon, Splitwise, Simple Note,
file system, or another non-Venmo app, stop consulting this wiki and solve from
the AppWorld prompt and API docs.

If the current task is a Venmo task involving contacts, relationships, social
feed transactions, or payment requests, read only:

```text
tasks/appworld-venmo-decision-table__subtask.md
```

After reading that decision page, start the task. Do not read a full skill
unless the decision page is insufficient for the exact action.

## Transfer Rules

- Transfer workflow shapes, not literals. Never reuse source task IDs, dates,
  names, emails, transaction IDs, request IDs, credentials, or access tokens.
- If the action differs, do not run the old skill. Reuse only the relevant
  sub-step, such as contact filtering, time-window filtering, or pagination.
- For answer-only tasks, do not call mutation APIs just because a related train
  trajectory used them.
- For mutation tasks, once you have the target record IDs, call the mutation API
  for all target IDs and `apis.supervisor.complete_task` in the same next code
  block when possible.
- Do not spend a separate turn summarizing wiki retrieval.

## Provenance

Each page links to the train trajectory or summary it came from. Use provenance
to audit a rule, not to import data into the current task.
