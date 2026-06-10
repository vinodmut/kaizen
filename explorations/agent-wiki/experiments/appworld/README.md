# AppWorld Agent-Wiki Experiment

This directory contains the first AppWorld-specific harness for testing whether
an agent-wiki helps the built-in AppWorld ReAct code agent.

## Goal

Evaluate both:

- **Success rate**: does an agent-wiki improve AppWorld task completion?
- **Cost**: does it reduce total model cost at similar or better success?

The baseline is AppWorld's existing `simplified_react_code_agent` without
memory or wiki.

## Split Discipline

Use strict split separation:

- Build wiki content only from `train` task trajectories.
- Evaluate on a held-out `dev` slice.
- Do not use test trajectories or test outputs for wiki construction.

For the first run, use a small slice:

- 20 train tasks for wiki construction.
- 20 dev tasks for evaluation.

Increase only after the pipeline is working end-to-end.

## Scripts

- `select_appworld_slice.py`: create a strict train/dev task-id manifest.
- `probe_wiki_filesystem_access.py`: check whether AppWorld's ReAct Python REPL
  can read a local wiki root.
- `agent_wiki_react_code_agent.py`: register the thin ReAct wrapper.
- `run_wiki_react_experiment.py`: run one arm on one task, a slice manifest, or
  the config's full dataset.
- `run_appworld_wiki_sweep.py`: run multiple arms over the same slice.
- `normalize_appworld_react_logs.py`: convert fresh AppWorld ReAct logs with
  `lm_calls.jsonl` into normalized trajectory JSON for wiki construction.
- `evaluate_appworld_slice.py`: evaluate exactly the task ids in a slice
  manifest.
- `summarize_appworld_runs.py`: summarize success, cost, token, step, API-call,
  and wiki-access signals across arms.

## Agent Integration

The wrapper in `agent_wiki_react_code_agent.py` subclasses AppWorld's
`SimplifiedReActCodeAgent` and changes only task initialization.

It does **not** implement a separate retrieval algorithm. Instead, it appends a
short instruction to the task prompt telling the ReAct agent to consult:

```text
<wiki-root>/AGENTS.md
```

and follow that wiki's own retrieval procedure. This keeps the experiment true
to the agent-wiki design: the wiki is an agent-readable memory surface, not just
a database behind custom retrieval code.

## Arms

Run the same held-out dev slice across:

- `baseline`: original AppWorld ReAct agent, no wiki.
- `guidelines`: wiki with atomic/cluster guidelines only.
- `skills`: wiki with skills only.
- `both`: wiki with skills and guidelines.
- `pruned`: wiki with skills plus uncovered guidelines.

Each non-baseline arm points `AgentWikiReActCodeAgent` at a different wiki root.

## Setup

Install AppWorld and download its data outside this exploration if needed. The
scripts expect AppWorld's usual `APPWORLD_ROOT` layout:

```text
<APPWORLD_ROOT>/
  data/
  experiments/
    outputs/
```

For this repo's downloaded data, use:

```bash
export APPWORLD_ROOT="$PWD/benchmark-data/appworld"
```

Use an AppWorld simplified ReAct config as the base config. A Jsonnet config can
be passed directly; `run_wiki_react_experiment.py` fills AppWorld's Jsonnet
external variables from the installed AppWorld package unless the corresponding
environment variables are already set.

## Step 1: Select Slices

Create a strict train/dev manifest:

```bash
uv run python explorations/agent-wiki/experiments/appworld/select_appworld_slice.py \
  --train-count 20 \
  --dev-count 20 \
  --seed 7 \
  --out explorations/agent-wiki/experiments/appworld/slices/small-20.json
```

This requires `appworld` to be installed and data downloaded.

## Step 2: Collect And Normalize Train Trajectories

Run the baseline ReAct agent on the train slice with `log_lm_calls=true` in the
AppWorld config. Then normalize those logs:

```bash
uv run python explorations/agent-wiki/experiments/appworld/normalize_appworld_react_logs.py \
  --appworld-root "$APPWORLD_ROOT" \
  --experiment-name aw_react_train20_baseline \
  --task-ids-file explorations/agent-wiki/experiments/appworld/slices/small-20.json \
  --manifest-split train \
  --out-dir trajectories/normalized/appworld-train20/items
```

The normalizer uses `lm_calls.jsonl` when present because it preserves the
ReAct assistant text where the agent plans, reasons about API outputs, and
decides what code to execute next. If `lm_calls.jsonl` and `logger.jsonl` are
both missing, the task is skipped by default because API-call logs alone are not
enough for high-quality wiki extraction.

## Step 3: Build Wiki Roots From Train Trajectories

Use only train trajectories to build the wiki roots. For the first AppWorld
experiment, create one wiki root per non-baseline arm:

```text
explorations/agent-wiki/wikis/appworld-guidelines/
explorations/agent-wiki/wikis/appworld-skills/
explorations/agent-wiki/wikis/appworld-both/
explorations/agent-wiki/wikis/appworld-pruned/
```

Each wiki root must contain `AGENTS.md`. The wrapper relies on the wiki's own
retrieval instructions; it does not implement retrieval outside the agent.

## Step 4: Probe Wiki Access

AppWorld's prompt discourages OS file access, and the execution environment may
block it. Before running a paid experiment, probe whether the ReAct Python REPL
can read local wiki files:

```bash
uv run python explorations/agent-wiki/experiments/appworld/probe_wiki_filesystem_access.py \
  --task-id <train-or-dev-task-id> \
  --wiki-root <wiki-root>
```

Interpretation:

- If the probe can read `AGENTS.md`, use `wiki_access_mode=direct_file`.
- If not, `wiki_access_mode=prompt_index` can inject `AGENTS.md` and
  `_index.jsonl`, but it is weaker because the agent cannot read selected page
  bodies. Prefer a later AppWorld-native file-system exposure if direct reads
  are blocked.

## Step 5: Run One Arm

The wrapper runner imports `agent_wiki_react_code_agent.py` so the new agent
type is registered, then delegates to AppWorld's `run_experiment`.

Baseline:

```bash
uv run python explorations/agent-wiki/experiments/appworld/run_wiki_react_experiment.py \
  --config /path/to/rendered-or-jsonnet/appworld-config.jsonnet \
  --experiment-name aw_react_baseline_dev20 \
  --task-ids-file explorations/agent-wiki/experiments/appworld/slices/small-20.json \
  --manifest-split dev \
  --arm baseline
```

Wiki arm:

```bash
uv run python explorations/agent-wiki/experiments/appworld/run_wiki_react_experiment.py \
  --config /path/to/rendered-or-jsonnet/appworld-config.jsonnet \
  --experiment-name aw_react_skills_dev20 \
  --task-ids-file explorations/agent-wiki/experiments/appworld/slices/small-20.json \
  --manifest-split dev \
  --arm skills \
  --wiki-root explorations/agent-wiki/wikis/appworld-skills
```

Shard a slice across processes by passing the same `--num-processes` and
different `--process-index` values.

## Step 6: Run All Arms

Use the sweep helper when all wiki roots are ready:

```bash
uv run python explorations/agent-wiki/experiments/appworld/run_appworld_wiki_sweep.py \
  --config /path/to/rendered-or-jsonnet/appworld-config.jsonnet \
  --task-ids-file explorations/agent-wiki/experiments/appworld/slices/small-20.json \
  --manifest-split dev \
  --experiment-prefix aw_react_dev20 \
  --wiki-root guidelines=explorations/agent-wiki/wikis/appworld-guidelines \
  --wiki-root skills=explorations/agent-wiki/wikis/appworld-skills \
  --wiki-root both=explorations/agent-wiki/wikis/appworld-both \
  --wiki-root pruned=explorations/agent-wiki/wikis/appworld-pruned
```

This creates experiment names:

```text
aw_react_dev20_baseline
aw_react_dev20_guidelines
aw_react_dev20_skills
aw_react_dev20_both
aw_react_dev20_pruned
```

## Step 7: Evaluate The Slice

Evaluate each arm on the exact dev slice:

```bash
uv run python explorations/agent-wiki/experiments/appworld/evaluate_appworld_slice.py \
  --experiment-name aw_react_dev20_baseline \
  --task-ids-file explorations/agent-wiki/experiments/appworld/slices/small-20.json \
  --manifest-split dev \
  --evaluation-name dev20
```

Repeat for the non-baseline experiment names.

## Step 8: Summarize

Generate an ASCII summary table plus optional JSON/Markdown artifacts:

```bash
uv run python explorations/agent-wiki/experiments/appworld/summarize_appworld_runs.py \
  --appworld-root "$APPWORLD_ROOT" \
  --task-ids-file explorations/agent-wiki/experiments/appworld/slices/small-20.json \
  --manifest-split dev \
  --run baseline=aw_react_dev20_baseline \
  --run guidelines=aw_react_dev20_guidelines \
  --run skills=aw_react_dev20_skills \
  --run both=aw_react_dev20_both \
  --run pruned=aw_react_dev20_pruned \
  --out-md explorations/agent-wiki/experiments/appworld/results/aw_react_dev20.md \
  --out-json explorations/agent-wiki/experiments/appworld/results/aw_react_dev20.json
```

## Metrics

Primary:

- AppWorld task success.
- Total model cost.

Secondary:

- Prompt/completion tokens.
- Number of ReAct steps.
- API calls.
- Whether the agent attempted to read wiki files.
- Which wiki root/arm was used.

## Notes

The downloaded public AppWorld experiment outputs in `benchmark-data/appworld`
preserve evaluation and API-call logs, but not full ReAct reasoning text in the
normalized artifacts. For wiki construction, run fresh train trajectories with
LM-call logging enabled so summaries/guidelines/skills can be grounded in the
actual ReAct code and observations.

The wrapper injects one instruction block into the final task user message. It
does not change the AppWorld APIs, task evaluator, ReAct loop, or model calling
logic.
