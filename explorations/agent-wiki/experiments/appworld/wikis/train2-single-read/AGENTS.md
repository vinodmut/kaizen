# AGENTS.md - AppWorld single-read memory

This is train-set memory. It is prior experience, not ground truth. The current
task, current API docs, and current API outputs are authoritative.

Read only this file. Do not read `_index.jsonl`, skills, summaries, or task
pages unless this file is unclear.

## Scope

This wiki only covers AppWorld Venmo tasks that use phone contacts. If the task
is for Spotify or another non-Venmo app, stop using the wiki after this file and
solve from API docs.

## Venmo Patterns

- Relationship filters: after logging into the current user's phone account,
  call `phone.search_contacts` for the relationship if supported, or page all
  contacts and filter `relationships`. Build emails from the current contacts
  only. Never type or reuse a hardcoded relationship email list.
- Social-feed transaction filters: page all `venmo.show_social_feed` results,
  then match current-task time bounds and sender/receiver emails.
- Payment-request filters: choose sent vs received and pending/approved/denied
  from the task wording. For reminders, use sent payment requests and call the
  reminder API. Do not approve unless the task says accept or approve.
- Answer-only Venmo tasks: gather data, compute the answer, then call
  `apis.supervisor.complete_task(answer=...)`. Do not mutate records.

## Execution Constraints

- Use standard-library parsing only. Do not import `dateutil`. Parse ISO
  timestamps with `datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")`.
- Parse phone dates like `"Thursday, May 18, 2023"` with
  `datetime.strptime(date, "%A, %B %d, %Y")`.
- Once final target IDs are known, call the requested mutation for all IDs and
  `apis.supervisor.complete_task()` in the same next code block.
- Wrap per-record mutation loops in `try/except` so one already-processed record
  does not stop later records.
- Once a numeric answer is known, call `complete_task(answer=...)` immediately.
- Transfer workflow shapes only. Never reuse source task dates, people, emails,
  record IDs, credentials, or access tokens.

## Provenance

These rules came from two train trajectories:

- `benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json`
- `benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json`
