# Single-Read Wiki Run

Date: 2026-06-10

## Change Tried

Created `explorations/agent-wiki/experiments/appworld/wikis/train2-single-read`
from `train2-compact-routing`.

The idea was to remove one more retrieval turn and make the memory usable from
the first `AGENTS.md` read:

- `AGENTS.md` now contains all routing, Venmo patterns, and execution
  constraints.
- It explicitly says not to read `_index.jsonl`, skills, summaries, or task
  pages unless unclear.
- It includes AppWorld-specific execution constraints discovered in prior runs:
  - do not import `dateutil`;
  - parse ISO timestamps with `datetime.strptime`;
  - recompute relationship emails from the current user's phone account;
  - wrap per-record mutation loops in `try/except`;
  - call `complete_task` immediately once the answer or target IDs are known.

This variant keeps the wrapper change from compact routing: the wrapper only
suggests reading `AGENTS.md` and does not force `_index.jsonl`.

## Evaluation

Slice: `benchmark-data/appworld-agent-wiki/slices/hard-dev-4.json`

Experiment: `aw_react_harddev4_single_read`

Generated ignored result artifacts:

- `benchmark-data/appworld-agent-wiki/results/harddev4-with-single-read.md`
- `benchmark-data/appworld-agent-wiki/results/harddev4-with-single-read.json`

```text
arm              experiment                         present  eval  success  cost  tokens   steps  api_calls  wiki_tasks
---------------  ---------------------------------  -------  ----  -------  ----  -------  -----  ---------  ----------
baseline         aw_react_harddev4_baseline         4        4     50.0%    1.15  562030   17.25  120.00     0
guidelines       aw_react_harddev4_guidelines       4        4     50.0%    1.24  600927   19.25  44.50      4
hand_skills      aw_react_harddev4_skills           4        4     50.0%    1.35  658465   19.50  58.75      4
skill_workflow   aw_react_harddev4_skill_workflow   4        4     0.0%     1.38  669478   19.50  60.00      4
guarded_core     aw_react_harddev4_guarded_core     4        4     50.0%    2.25  1108447  19.00  50.75      4
compact_routing  aw_react_harddev4_compact_routing  4        4     50.0%    1.22  593301   19.50  52.25      4
single_read      aw_react_harddev4_single_read      4        4     75.0%    0.88  423759   15.75  61.50      4
```

Per-task single-read outcomes:

```text
task_id     success  steps  api_calls  cost     tokens
----------  -------  -----  ---------  -------  ------
df61dc5_3   false    13     64         0.16330  77942
4fab96f_2   true     16     30         0.23013  111292
383cbac_3   true     14     85         0.18118  86734
6171bbc_3   true     20     67         0.30343  147791
```

Per-task success pattern:

```text
task_id     baseline  compact_routing  single_read
----------  --------  ---------------  -----------
df61dc5_3   fail      fail             fail
4fab96f_2   success   success          success
383cbac_3   success   fail             success
6171bbc_3   fail      success          success
```

## What Improved

Single-read is the first arm in this slice to beat the baseline and prior wiki
arms:

- Success improved to 3/4.
- Cost dropped to $0.88, below baseline's $1.15.
- Tokens dropped to 423,759, below baseline's 562,030.
- Average steps dropped to 15.75, below baseline's 17.25.

The inline execution constraints fixed the compact-routing regression on
`383cbac_3`: the agent avoided `dateutil`, computed the answer, and called
`complete_task(answer=...)` at step 14.

The non-Venmo routing stayed cheap: the Spotify task read only `AGENTS.md`, then
solved from API docs and succeeded.

## Remaining Failure

`df61dc5_3` still failed, but the failure changed. The agent completed in 13
steps and made the right kind of mutation, but liked the wrong transaction IDs.
It filtered transactions whose `created_at` year was `2023`:

```python
txn_year = datetime.strptime(txn["created_at"], "%Y-%m-%dT%H:%M:%S").year
if txn_year == 2023:
    ...
```

The expected ID set appears to include transactions from the ongoing one-year
window ending at the AppWorld current date, not just the calendar year. With a
current date of May 18, 2023, that means the intended lower bound is around
May 18, 2022, not January 1, 2023.

Next targeted rule to test:

- For AppWorld phrases like "ongoing year", do not assume calendar year. Get
  the current date and interpret it as the current rolling one-year period
  unless the task explicitly says "this calendar year" or names a year.

This is a much narrower memory update than the earlier retrieval fixes.
