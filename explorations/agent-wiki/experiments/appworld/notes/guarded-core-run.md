# Guarded Core Wiki Run

Date: 2026-06-10

## Change Tried

Created `explorations/agent-wiki/experiments/appworld/wikis/train2-guarded-core`
from the generated `train2-skill-workflow` wiki.

Changes:

- Replaced generic `AGENTS.md` with a compact AppWorld-specific retrieval
  contract.
- Added `tasks/appworld-venmo-decision-table__subtask.md`, derived only from
  the two train trajectories.
- Added explicit `Applies When` and `Does Not Apply When` sections to both
  generated Venmo skills.
- Rebuilt the wiki catalog with `build_agent_wiki.py ... catalog`.

The wrapper was unchanged: the AppWorld ReAct agent still self-retrieves by
reading wiki files according to `AGENTS.md`.

## Evaluation

Slice: `benchmark-data/appworld-agent-wiki/slices/hard-dev-4.json`

Experiment: `aw_react_harddev4_guarded_core`

Generated ignored result artifacts:

- `benchmark-data/appworld-agent-wiki/results/harddev4-with-guarded-core.md`
- `benchmark-data/appworld-agent-wiki/results/harddev4-with-guarded-core.json`

```text
arm             experiment                        present  eval  success  cost  tokens   steps  api_calls  wiki_tasks
--------------  --------------------------------  -------  ----  -------  ----  -------  -----  ---------  ----------
baseline        aw_react_harddev4_baseline        4        4     50.0%    1.15  562030   17.25  120.00     0
guidelines      aw_react_harddev4_guidelines      4        4     50.0%    1.24  600927   19.25  44.50      4
hand_skills     aw_react_harddev4_skills          4        4     50.0%    1.35  658465   19.50  58.75      4
skill_workflow  aw_react_harddev4_skill_workflow  4        4     0.0%     1.38  669478   19.50  60.00      4
guarded_core    aw_react_harddev4_guarded_core    4        4     50.0%    2.25  1108447  19.00  50.75      4
```

Per-task guarded-core outcomes:

```text
task_id     success  steps  api_calls  cost     tokens
----------  -------  -----  ---------  -------  ------
df61dc5_3   false    20     38         0.37577  183559
4fab96f_2   false    20     16         0.39801  194867
383cbac_3   true     16     84         1.14803  569378
6171bbc_3   true     20     65         0.32889  160643
```

Per-task success pattern:

```text
task_id     baseline  guidelines  hand_skills  skill_workflow  guarded_core
----------  --------  ----------  -----------  --------------  ------------
df61dc5_3   fail      success     fail         fail            fail
4fab96f_2   success   fail        fail         fail            fail
383cbac_3   success   fail        success      fail            success
6171bbc_3   fail      success     success      fail            success
```

## What This Shows

The guarded wiki fixed the worst failure mode of the fully generated skill
workflow: it no longer drove the run to 0/4. It recovered to 2/4 and succeeded
on the answer-only Venmo dinner task (`383cbac_3`) and the unrelated Spotify
task (`6171bbc_3`).

The change did not improve the overall best success rate. It matched the
hand-skills arm's 2/4 success pattern, but at higher cost.

The main remaining problem is step budget. Both failing guarded-core tasks
hit the 20-step limit before making the required mutations:

- `df61dc5_3`: found 29 transactions to like but spent step 20 inspecting
  `venmo.like_transaction`, so no likes were applied.
- `4fab96f_2`: reached date/contact setup by step 20, but never sent reminder
  notifications.

The retrieval guard helped with action mismatch, but file-based self-retrieval
still consumes too many ReAct turns:

- Venmo-like task read `AGENTS.md`, `_index.jsonl`, the decision table, and the
  like skill before starting app work.
- Spotify task correctly found no Spotify skill, but still read `AGENTS.md`,
  `_index.jsonl`, and a generic pagination cluster. It succeeded anyway, but
  this was still overhead.

## Next Fix

Reduce retrieval turns before adding more wiki content.

Recommended changes:

1. Make `AGENTS.md` the only required initial read.
2. Remove the wrapper's unconditional instruction to read `_index.jsonl` after
   `AGENTS.md`; let `AGENTS.md` decide whether the index is needed.
3. For small direct-file wikis, consider inlining the compact retrieval contract
   in the injected prompt and using file reads only for selected pages.
4. Keep the decision page, but do not read a full skill when the decision page
   already contains enough procedural guidance.
5. Add a "mutation urgency" instruction for AppWorld: once the agent has the
   target IDs, execute the mutation and `complete_task` in the same next code
   block instead of inspecting another already-known API unless genuinely
   uncertain.

This suggests the agent-wiki content is directionally useful, but the current
ReAct integration turns memory retrieval into too many tool steps. The next
experiment should optimize retrieval cost/steps before generating more
memories.
