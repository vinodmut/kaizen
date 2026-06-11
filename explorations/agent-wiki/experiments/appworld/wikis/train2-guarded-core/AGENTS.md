# AGENTS.md - AppWorld wiki retrieval contract

This wiki is AppWorld train-set memory. Treat it as prior experience, not as
ground truth. The current task prompt, current API docs, and current API outputs
are authoritative.

## Read Budget

Use the wiki only after reading the actual task request.

1. Read `_index.jsonl`.
2. Identify the requested app(s), action, data source, relation filters, and
   time filters.
3. If no row matches both the app and action family, stop consulting the wiki
   and solve from the AppWorld prompt and API docs.
4. If there is a match, read at most:
   - one compact decision page, and
   - one directly matching skill or cluster.

Do not read every wiki page. Do not use wiki time, IDs, credentials, people, or
record values in the current task.

## AppWorld-Specific Routing

This small wiki currently has useful evidence for Venmo tasks that also use
phone contacts:

- Venmo social-feed transaction tasks that filter by a contact relationship and
  a time range.
- Venmo payment-request tasks that filter by a contact relationship and then
  accept/approve received pending requests.

For Venmo tasks, first read:

```text
tasks/appworld-venmo-decision-table__subtask.md
```

Then read a skill only if the skill's action matches the current task:

- Read `skills/like-venmo-transactions-involving-relatives/SKILL.md` only when
  the task asks you to like Venmo transactions.
- Read `skills/accept-venmo-payment-requests-from-contacts/SKILL.md` only when
  the task asks you to accept or approve received pending Venmo payment
  requests.

If the task is about Spotify, Gmail, Todoist, Amazon, Splitwise, Simple Note,
file system, or another app not covered by the index, do not read app-specific
pages from this wiki.

## Transfer Rules

- Transfer workflow shapes, not literals. Never reuse source task IDs, dates,
  names, emails, transaction IDs, request IDs, credentials, or access tokens.
- If the action differs, do not run the old skill. Use only the relevant
  sub-step, such as contact relationship filtering or pagination.
- For answer-only tasks, do not call mutation APIs just because a related skill
  used them.
- For mutation tasks, make the smallest requested mutation and then call
  `apis.supervisor.complete_task`.

## Provenance

Each page links to the train trajectory or summary it came from. Use provenance
to audit a rule, not to import data into the current task.
