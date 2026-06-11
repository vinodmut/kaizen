# Compact Routing Wiki Run

Date: 2026-06-10

## Change Tried

Created `explorations/agent-wiki/experiments/appworld/wikis/train2-compact-routing`
from `train2-guarded-core`.

Changes:

- Updated `agent_wiki_react_code_agent.py` so the direct-file prompt no longer
  tells the agent to read `_index.jsonl` after `AGENTS.md`.
- Replaced the wiki's `AGENTS.md` with compact routing:
  - non-Venmo tasks stop after `AGENTS.md`;
  - Venmo/contact tasks read only
    `tasks/appworld-venmo-decision-table__subtask.md`;
  - `_index.jsonl` is only a fallback if `AGENTS.md` is unclear.
- Updated the Venmo decision page so it is the main procedural memory, not just
  a pre-skill router.
- Added a step-budget rule: after target IDs are known, execute the mutation
  and `complete_task` in the same next code block when possible.

## Evaluation

Slice: `benchmark-data/appworld-agent-wiki/slices/hard-dev-4.json`

Experiment: `aw_react_harddev4_compact_routing`

Generated ignored result artifacts:

- `benchmark-data/appworld-agent-wiki/results/harddev4-with-compact-routing.md`
- `benchmark-data/appworld-agent-wiki/results/harddev4-with-compact-routing.json`

```text
arm              experiment                         present  eval  success  cost  tokens   steps  api_calls  wiki_tasks
---------------  ---------------------------------  -------  ----  -------  ----  -------  -----  ---------  ----------
baseline         aw_react_harddev4_baseline         4        4     50.0%    1.15  562030   17.25  120.00     0
guidelines       aw_react_harddev4_guidelines       4        4     50.0%    1.24  600927   19.25  44.50      4
hand_skills      aw_react_harddev4_skills           4        4     50.0%    1.35  658465   19.50  58.75      4
skill_workflow   aw_react_harddev4_skill_workflow   4        4     0.0%     1.38  669478   19.50  60.00      4
guarded_core     aw_react_harddev4_guarded_core     4        4     50.0%    2.25  1108447  19.00  50.75      4
compact_routing  aw_react_harddev4_compact_routing  4        4     50.0%    1.22  593301   19.50  52.25      4
```

Per-task compact-routing outcomes:

```text
task_id     success  steps  api_calls  cost     tokens
----------  -------  -----  ---------  -------  ------
df61dc5_3   false    20     86         0.31961  155155
4fab96f_2   true     18     30         0.28953  140131
383cbac_3   false    20     11         0.28583  138498
6171bbc_3   true     20     82         0.32827  159517
```

Per-task success pattern:

```text
task_id     baseline  guidelines  hand_skills  guarded_core  compact_routing
----------  --------  ----------  -----------  ------------  ---------------
df61dc5_3   fail      success     fail         fail          fail
4fab96f_2   success   fail        fail         fail          success
383cbac_3   success   fail        success      success       fail
6171bbc_3   fail      success     success      success       success
```

## What Improved

Compact routing achieved the intended retrieval behavior:

- Venmo tasks read `AGENTS.md` and the decision table.
- They did not read `_index.jsonl`.
- They did not read full `SKILL.md` files.
- The Spotify task read only `AGENTS.md` and then stopped consulting the wiki.

This brought cost and tokens back close to baseline:

- `guarded_core`: $2.25, 1,108,447 tokens
- `compact_routing`: $1.22, 593,301 tokens
- `baseline`: $1.15, 562,030 tokens

The step-budget rule fixed `4fab96f_2`: the agent found the reminder target IDs
and used the remaining turn to call `venmo.remind_payment_request` for all of
them and complete the task.

## What Got Worse

`383cbac_3` regressed. It reached step 20 without completing the answer. The
immediate issue was an avoidable `dateutil` import, which AppWorld disallowed:

```text
Usage of the following module is not allowed: dateutil.
```

This is not a retrieval error; it is a procedural AppWorld issue. The wiki
should probably include a compact AppWorld code constraint: parse ISO timestamps
with `datetime.strptime`, not external modules.

`df61dc5_3` made the requested mutation but liked the wrong transaction IDs. It
passed all mutation-shape tests except the exact ID set. The logs show it used a
hardcoded coworker email list from earlier contact state instead of deriving the
current task's coworker emails correctly. This suggests the wiki should say:

- never hardcode relationship emails after a previous API call;
- keep `coworker_emails` derived only from the current user's phone contacts;
- do not continue from partial or stale contact variables if a login/profile
  step changes the active account.

## Interpretation

The compact routing change did what it was supposed to do: it reduced retrieval
cost and removed unnecessary index/skill reads. It did not increase aggregate
success on this tiny slice, but it changed the failure modes from "wiki
retrieval consumes the run" to ordinary AppWorld execution mistakes.

Next iteration should add a small AppWorld execution-constraints page or inline
rules:

- Use only standard-library modules allowed by AppWorld; parse timestamps with
  `datetime.strptime`.
- Treat relationship email sets as per-user/per-task and recompute them after
  logging into the current user's phone account.
- If a mutating loop can fail on one already-processed record, wrap each call in
  `try/except` from the start so later records still execute.
- For answer-only tasks, prioritize `complete_task(answer=...)` once a numeric
  answer is available.

This should be tested with the same compact routing wrapper, not by returning to
full index/skill reads.
