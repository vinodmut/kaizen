---
name: agent-wiki-extract-evidence
description: Extract domain-agnostic event and sequence evidence from normalized agent trajectories before guideline or skill synthesis.
---

# Agent Wiki - Extract Evidence

## Purpose

Capture what visibly happened in one trajectory as reusable evidence units.
This pass is observational. Do not derive guidelines, name domains, classify
benchmark tasks, or promote skills here. Later passes cluster and abstract
patterns from the evidence.

Evidence is audit/provenance material. It can support future guidelines and
skills, but it is not direct advice and should not be recall-preferred.

## Input

A single normalized trajectory JSON file, plus a target `--wiki-root`.

Read:

- `session_id`, `agent`, `model`
- `openai_chat_completion.messages`
- `stats`
- `source.transcript_path` and `source.trajectory_path` when present
- `recalled_guidelines` only as observation of what was available to the agent

Do not read evaluator output, scores, references, expected outputs, hidden
schemas, or benchmark-specific result files.

## Non-Leakage Contract

Evidence must be domain-agnostic at the normalized-pattern level. Do not
hardcode tool names, domain names, benchmark categories, task classes, expected
answers, evaluator behavior, reference files, hidden schemas, task ids, or gold
labels.

Observed commands, filenames, schema keys, and outputs may be retained only in
short source snippets when needed for provenance. The normalized observation
must abstract them into generic roles such as input artifact, generated artifact,
checker, operation, observation, failure, retry, assumption change, or final
result.

Do not create a fixed taxonomy of benchmark-specific categories. The `kind`
field is a small structural label only. Let `pattern` and `sequence` describe
what happened in neutral language.

## What To Extract

For each trajectory, emit 5 to 20 evidence items. Prefer items that show
process structure:

- attempts, observations, failures, retries, and resolutions
- sequence motifs, such as inspect, transform, verify
- state transitions, such as assumption, contradiction, revised action
- artifact relationships, such as source artifact, derived artifact, validation
- decision points, including why an approach changed
- verification behavior, including whether the final result was checked
- repeated actions that did not add new information
- setup or environment assumptions that were confirmed or contradicted

Skip items that are only task facts, answer facts, domain facts, hidden
evaluation details, or exact source-data values.

## Output Schema

Build one JSON object:

```json
{
  "items": [
    {
      "id": "<optional stable 12-hex id>",
      "kind": "event | sequence | transition | artifact_relation | verification",
      "title": "Short audit title",
      "summary": "One sentence observation.",
      "session_id": "<session id>",
      "agent": "<source agent>",
      "normalized_path": "<relative path>",
      "related_summary": "summaries/<sid>.md",
      "span": {
        "message_start": 0,
        "message_end": 0
      },
      "pattern": "Domain-neutral description of the observed pattern.",
      "sequence": ["observe", "act", "check"],
      "precondition": "What was true before this happened.",
      "action": "What the agent did, abstracted.",
      "outcome": "What changed or was learned.",
      "statement": "What was observed. No prescriptive rule.",
      "evidence": "Short trajectory-visible support, redacted where needed.",
      "leakage_notes": "Why this item is safe, or why raw details were omitted.",
      "tags": ["short", "domain-agnostic"],
      "sources": [
        {
          "path": "<normalized path>",
          "kind": "normalized-json",
          "message_start": 0,
          "message_end": 0,
          "tool_call_id": "<optional>",
          "quote": "short excerpt"
        }
      ],
      "supports": [
        {
          "kind": "guideline | skill | cluster",
          "id": "<optional target id>",
          "link": "<optional wiki-relative link>"
        }
      ]
    }
  ]
}
```

Allowed `kind` values are structural, not topical:

- `event`
- `sequence`
- `transition`
- `artifact_relation`
- `verification`

Use short, generic tags. Do not use task names, domains, specific tool names,
exact filenames, or benchmark labels as tags.

Use `supports` only when a later repair or audit pass can link an evidence item
to a generated guideline, skill, or cluster. Normal per-session evidence
extraction can omit it.

## Render

Write the payload through the helper:

```bash
cat /tmp/evidence-payload.json | uv run python explorations/agent-wiki/skills/scripts/build_agent_wiki.py --wiki-root <wiki-root> render-evidence
```

Do not run `catalog`. The ingest orchestrator runs it once at the end.

## Quality Gate

Before rendering, check each item:

1. Can this be understood as process evidence on unrelated tasks?
2. Is any source-specific detail limited to a short provenance quote?
3. Does the normalized statement avoid task names, domains, answer values, exact
   output filenames, evaluator behavior, hidden schemas, and benchmark labels?
4. Is it observational rather than prescriptive?
5. Does it point back to message spans or source snippets for audit?

If an item fails the gate, omit it.
