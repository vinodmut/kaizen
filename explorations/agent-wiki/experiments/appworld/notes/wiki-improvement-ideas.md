# AppWorld Wiki Improvement Ideas

Context: the `train2-skill-workflow` wiki was built from two successful train
trajectories. On the 4-task hard dev slice it was worse than the earlier arms:
it was consulted on every task, added cost and steps, and scored 0/4. The most
likely issue is not that the memories are useless, but that the wiki retrieval
contract is too broad for a small, Venmo-heavy wiki.

## Ideas to Try First

1. Add a "no relevant memory" path.
   - The agent should stop consulting the wiki when the requested app or action
     family is absent from `_index.jsonl`.
   - This should reduce wasted reads on unrelated apps such as Spotify.

2. Split generic AppWorld rules from app/domain skills.
   - Generic rules like pagination, credentials, contacts, and API docs are
     already in the task prompt. Repeating them costs tokens.
   - App/domain pages should be read only when the app and action match.

3. Add strict applicability metadata to skills.
   - Each skill should say when it applies and when it does not.
   - Especially distinguish "approve payment request" from "remind payment
     request", and "like transactions" from "answer a question about
     transactions".

4. Add compact decision tables.
   - For Venmo, the useful train evidence can be represented as app/action
     patterns:
     - social feed + relation + time range + like action
     - received payment requests + relation + accept action
   - Decision tables are cheaper and safer than reading full skills for every
     related task.

5. Capture failure modes, not just happy paths.
   - Successful trajectories show what worked, but the dev failures show where
     transfer goes wrong: wrong action reuse, wrong temporal filtering, wrong
     aggregation, and step-budget overrun.
   - These should become provenance-linked "avoid" notes after evaluation,
     kept separate from train-derived wiki content when strict split matters.

6. Add evidence-bound API snippets.
   - Skills should name only API calls that appeared in the source trajectory
     or returned API docs.
   - Avoid emitting executable helper scripts that depend on AppWorld runtime
     variables unless they were validated inside the target runtime.

7. Compress the retrieval contract.
   - `AGENTS.md` should be short enough to read once and should cap follow-up
     page reads.
   - The agent should read at most one compact decision page and one matching
     skill/cluster before starting the task.

8. Add `applies_when` and `does_not_apply_when`.
   - These should be visible in the page body, not only frontmatter, because
     the agent may not parse YAML carefully.

9. Use eval feedback as wiki input in a separate loop.
   - Keep train-only wiki construction strict for benchmark scoring.
   - Separately, build a "postmortem" wiki from failed dev runs to learn what
     memory types are missing.

10. Add quality gates before paid evaluation.
    - Run a cheap retrieval simulation against task prompts.
    - Confirm unrelated tasks select no app-specific page and related tasks
      select the right page with the right action.

## Recommended Next Iteration

Create a `train2-guarded-core` wiki variant from the generated train wiki:

- Replace generic `AGENTS.md` with an AppWorld-specific retrieval contract.
- Add a compact Venmo decision table derived only from train trajectories.
- Edit the two generated Venmo skills to include explicit applies/does-not-apply
  sections.
- Run the same 4-task hard dev slice and compare success, cost, token count,
  steps, API calls, and wiki-access signals.
