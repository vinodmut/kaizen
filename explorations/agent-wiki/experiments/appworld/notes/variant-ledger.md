# AppWorld Wiki Variant Ledger

Date: 2026-06-11

This ledger records the AppWorld hard-dev-4 wiki variants tried so far. The
evaluation slice is:

```text
benchmark-data/appworld-agent-wiki/slices/hard-dev-4.json
```

Raw AppWorld outputs and summary JSON/Markdown are under ignored
`benchmark-data/` paths. The wiki variants and notes are under
`explorations/agent-wiki/experiments/appworld/`.

## Variants

```text
variant           wiki / source                                                experiment
---------------   ----------------------------------------------------------   ---------------------------------
baseline          no wiki                                                      aw_react_harddev4_baseline
guidelines        benchmark-data/appworld-agent-wiki/wikis/train2-guidelines   aw_react_harddev4_guidelines
hand_skills       benchmark-data/appworld-agent-wiki/wikis/train2-skills       aw_react_harddev4_skills
skill_workflow    wikis/train2-skill-workflow                                  aw_react_harddev4_skill_workflow
guarded_core      wikis/train2-guarded-core                                    aw_react_harddev4_guarded_core
compact_routing   wikis/train2-compact-routing                                 aw_react_harddev4_compact_routing
single_read       wikis/train2-single-read                                     aw_react_harddev4_single_read
```

## Summary Results

```text
arm              success  cost  tokens   avg steps  avg api calls
---------------  -------  ----  -------  ---------  -------------
baseline         50.0%    1.15  562030   17.25      120.00
guidelines       50.0%    1.24  600927   19.25       44.50
hand_skills      50.0%    1.35  658465   19.50       58.75
skill_workflow    0.0%    1.38  669478   19.50       60.00
guarded_core     50.0%    2.25  1108447  19.00       50.75
compact_routing  50.0%    1.22  593301   19.50       52.25
single_read      75.0%    0.88  423759   15.75       61.50
```

## Per-Task Success

```text
task_id     baseline  guidelines  hand_skills  skill_workflow  guarded_core  compact_routing  single_read
----------  --------  ----------  -----------  --------------  ------------  ---------------  -----------
df61dc5_3   fail      success     fail         fail            fail          fail             fail
4fab96f_2   success   fail        fail         fail            fail          success          success
383cbac_3   success   fail        success      fail            success       fail             success
6171bbc_3   fail      success     success      fail            success       success          success
```

Task descriptions:

```text
df61dc5_3  Like all Venmo transactions of the ongoing year to and from coworkers.
4fab96f_2  Send Venmo reminders for payment requests to coworkers older than 40 days.
383cbac_3  Answer how much manager paid at Whimsical Bites, including user's share.
6171bbc_3  Create Spotify playlist with most-played song from each playlist.
```

## What Changed By Variant

### skill_workflow

Wiki:

```text
explorations/agent-wiki/experiments/appworld/wikis/train2-skill-workflow
```

Built from two normalized train trajectories by running the agent-wiki skills
workflow. It produced summaries, atomic guidelines, clusters, and two Venmo
skills.

Result: 0/4. The generated skills were too broad and encouraged irrelevant or
overly expensive retrieval. The agent consulted the wiki on every task and
spent extra turns without improving execution.

### guarded_core

Wiki:

```text
explorations/agent-wiki/experiments/appworld/wikis/train2-guarded-core
```

Changes:

- Replaced generic `AGENTS.md` with AppWorld-specific retrieval rules.
- Added `tasks/appworld-venmo-decision-table__subtask.md`.
- Added `Applies When` / `Does Not Apply When` sections to generated Venmo
  skills.

Result: 2/4. It recovered from the generated skill workflow's 0/4, but cost and
tokens increased sharply. Failure mode moved to retrieval overhead and step
budget: the agent still read `AGENTS.md`, `_index.jsonl`, a decision page, and
sometimes a full skill.

Detailed note:

```text
explorations/agent-wiki/experiments/appworld/notes/guarded-core-run.md
```

### compact_routing

Wiki:

```text
explorations/agent-wiki/experiments/appworld/wikis/train2-compact-routing
```

Wrapper change:

```text
explorations/agent-wiki/experiments/appworld/agent_wiki_react_code_agent.py
```

The wrapper no longer tells the agent to read `_index.jsonl` after `AGENTS.md`.
It says to follow `AGENTS.md` and read only files needed for the exact task.

Wiki changes:

- `AGENTS.md` told non-Venmo tasks to stop after `AGENTS.md`.
- Venmo/contact tasks read only the Venmo decision page.
- Full `SKILL.md` reads were avoided.

Result: 2/4. Cost returned near baseline. It fixed the reminder task
(`4fab96f_2`) but regressed the answer-only Venmo task (`383cbac_3`) because
the agent imported banned `dateutil` and hit the step cap before completing.

Detailed note:

```text
explorations/agent-wiki/experiments/appworld/notes/compact-routing-run.md
```

### single_read

Wiki:

```text
explorations/agent-wiki/experiments/appworld/wikis/train2-single-read
```

Changes:

- Inlined routing, Venmo patterns, and execution constraints into `AGENTS.md`.
- Told the agent to read only `AGENTS.md`.
- Added constraints learned from prior variants:
  - do not import `dateutil`;
  - parse timestamps with `datetime.strptime`;
  - recompute relationship emails from the current user's phone account;
  - wrap per-record mutation loops in `try/except`;
  - call `complete_task` immediately once answer or target IDs are known.

Result: 3/4. This is the first wiki arm to beat baseline on both success and
cost. It reduced retrieval to one file read and changed the remaining failure
from step-budget failure to a narrow task-interpretation issue.

Remaining failure:

```text
df61dc5_3
```

The agent interpreted "ongoing year" as calendar year 2023. The expected set
appears to be a rolling one-year window ending at the AppWorld current date,
e.g. around May 18, 2022 to May 18, 2023.

Detailed note:

```text
explorations/agent-wiki/experiments/appworld/notes/single-read-run.md
```

## Current Best Variant

Use `single_read` as the current best AppWorld wiki approach:

```text
explorations/agent-wiki/experiments/appworld/wikis/train2-single-read
```

It has the best score on this slice:

```text
success: 75.0%
cost:    $0.88
tokens:  423759
steps:   15.75 average
```

## Next Targeted Idea

Add one narrow temporal interpretation rule to the single-read wiki:

```text
For AppWorld phrases like "ongoing year", do not assume calendar year. Get the
current date and interpret it as the rolling one-year period ending at the
current date unless the task explicitly says "calendar year" or names a year.
```

Then rerun the same 4-task slice. The expected improvement target is
`df61dc5_3`; avoid changing the single-read retrieval shape.
