#!/usr/bin/env python3
"""Run one agent-wiki skill pass with an LLM and render the resulting payload.

This is intentionally dataset-agnostic: it reads normalized trajectory JSON,
loads the relevant SKILL.md as the pass contract, asks an LLM for the JSON
payload that the deterministic renderer expects, then pipes that JSON into
build_agent_wiki.py.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from openai import OpenAI


REPO_ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = Path(__file__).resolve().with_name("build_agent_wiki.py")

PASS_TO_SKILL = {
    "summarize": "agent-wiki-summarize",
    "extract-guidelines": "agent-wiki-extract-guidelines",
    "synthesize-skill": "agent-wiki-synthesize-skill",
    "consolidate-guidelines": "agent-wiki-consolidate-guidelines",
}

PASS_TO_RENDER_CMD = {
    "summarize": "render-summary",
    "extract-guidelines": "render-guidelines",
    "synthesize-skill": "render-skill",
    "consolidate-guidelines": "render-cluster",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pass",
        required=True,
        choices=sorted(PASS_TO_SKILL),
        dest="pass_name",
        help="Agent-wiki pass to run.",
    )
    parser.add_argument("--wiki-root", required=True, type=Path)
    parser.add_argument("--trajectory", type=Path, help="Normalized trajectory JSON for per-trajectory passes.")
    parser.add_argument("--model", default=os.environ.get("AGENT_WIKI_MODEL", "Azure/gpt-4.1"))
    parser.add_argument("--payload-out", type=Path, help="Write the LLM JSON payload here.")
    parser.add_argument("--no-render", action="store_true", help="Only produce the payload; do not render it.")
    parser.add_argument("--rewrite", action="store_true", help="Forward --rewrite to render commands.")
    parser.add_argument("--archive-covered", action="store_true", help="Forward --archive-covered for synthesize-skill.")
    args = parser.parse_args()

    if args.pass_name != "consolidate-guidelines" and args.trajectory is None:
        raise SystemExit(f"--trajectory is required for {args.pass_name}")
    if args.pass_name == "consolidate-guidelines" and args.trajectory is not None:
        raise SystemExit("--trajectory is not used for consolidate-guidelines")

    payload = run_llm_pass(args)
    if args.payload_out:
        args.payload_out.parent.mkdir(parents=True, exist_ok=True)
        args.payload_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote payload: {args.payload_out}")

    if args.no_render:
        return 0
    return render_payload(args, payload)


def run_llm_pass(args: argparse.Namespace) -> Any:
    skill_name = PASS_TO_SKILL[args.pass_name]
    skill_md_path = SKILLS_ROOT / skill_name / "SKILL.md"
    skill_md = skill_md_path.read_text(encoding="utf-8")

    prompt = build_prompt(args, skill_md_path, skill_md)
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("ETE_LITELLM_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL") or os.environ.get("CODEX_MODEL_PROVIDER_BASE_URL"),
    )
    response = client.chat.completions.create(
        model=args.model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an agent-wiki pass worker. Follow the provided SKILL.md as the contract. "
                    "Use only evidence in the provided trajectory/wiki corpus. Output valid JSON only, "
                    "with no markdown fences and no commentary."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    text = response.choices[0].message.content or "{}"
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"LLM returned invalid JSON: {exc}\n{text[:2000]}") from exc


def build_prompt(args: argparse.Namespace, skill_md_path: Path, skill_md: str) -> str:
    existing = collect_existing(args.wiki_root)
    sections = [
        f"Run pass: {args.pass_name}",
        f"Skill file: {relpath(skill_md_path)}",
        "",
        "SKILL.md:",
        skill_md,
        "",
        f"Target wiki root: {relpath(args.wiki_root)}",
        "Existing wiki state:",
        json.dumps(existing, indent=2, sort_keys=True),
    ]

    if args.pass_name == "consolidate-guidelines":
        sections.extend(
            [
                "",
                "Guideline corpus from dump-guidelines:",
                json.dumps(dump_guidelines(args.wiki_root), indent=2, sort_keys=True),
                "",
                'Output schema: return {"clusters": [<render-cluster payload>, ...]}. '
                'Return {"clusters": []} if no real shared rule qualifies.',
            ]
        )
        return "\n".join(sections)

    trace = load_compact_trace(args.trajectory)
    sections.extend(
        [
            "",
            "Normalized trajectory JSON, compacted only to limit oversized tool outputs:",
            json.dumps(trace, indent=2, sort_keys=True),
            "",
            output_contract(args.pass_name),
            "",
            "Quality constraints:",
            "- Preserve provenance: include session_id, normalized_path, agent, and related_summary where the render schema supports them.",
            "- Do not invent task facts, results, tool names, command names, API names, or argument signatures.",
            "- If the trajectory involves an API/tool surface, mention concrete calls only when they appear verbatim in assistant code or returned documentation.",
            "- If a needed future call was not observed, instruct the future agent to inspect current documentation instead of guessing the call name.",
            "- For synthesize-skill, generalize the skill to the reusable workflow family instead of restating the exact original task.",
            "- For synthesize-skill, do not emit sibling scripts when the code depends on runtime objects that only exist inside the future agent environment, such as `apis`, browser/page handles, live sessions, or benchmark harness objects.",
            "- Prefer concise wiki content written for future agents, not a retelling of the whole transcript.",
        ]
    )
    return "\n".join(sections)


def output_contract(pass_name: str) -> str:
    if pass_name == "summarize":
        return (
            "Output schema: return one render-summary JSON object with fields "
            "session_id, agent, model, goal, outcome, duration_seconds, tools_used, "
            "narrative, key_turns, normalized_path, transcript_path, and optional recalled_guidelines."
        )
    if pass_name == "extract-guidelines":
        return (
            'Output schema: return {"entities": [...]} exactly as render-guidelines expects. '
            'Return {"entities": []} if the trajectory yields no reusable guidelines.'
        )
    if pass_name == "synthesize-skill":
        return (
            "Output schema: return one render-skill JSON object if a procedural skill qualifies. "
            'If no skill qualifies, return {"skip": true, "reason": "..."}.'
        )
    raise ValueError(pass_name)


def collect_existing(wiki_root: Path) -> dict[str, Any]:
    def names(glob: str) -> list[str]:
        return sorted(relpath(p) for p in wiki_root.glob(glob) if p.is_file())

    return {
        "summaries": names("summaries/*.md"),
        "guidelines": names("guidelines/*.md"),
        "skills": names("skills/*/SKILL.md"),
    }


def dump_guidelines(wiki_root: Path) -> list[dict[str, Any]]:
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--wiki-root", str(wiki_root), "dump-guidelines"],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout or "[]")
    return data if isinstance(data, list) else []


def load_compact_trace(path: Path | None) -> dict[str, Any]:
    if path is None:
        raise ValueError("path required")
    data = json.loads(path.read_text(encoding="utf-8"))
    messages = data.get("openai_chat_completion", {}).get("messages") or data.get("messages") or []
    compact_messages = []
    for index, msg in enumerate(messages):
        role = msg.get("role")
        content = msg.get("content")
        compact_messages.append(
            {
                "index": index,
                "role": role,
                "content": compact_content(content, keep_full=(role == "assistant")),
            }
        )
    return {
        "schema_version": data.get("schema_version"),
        "dataset": data.get("dataset"),
        "agent": data.get("agent"),
        "session_id": data.get("session_id") or data.get("metadata", {}).get("id"),
        "metadata": data.get("metadata"),
        "model": data.get("model"),
        "stats": data.get("stats"),
        "outcome": data.get("outcome"),
        "source": data.get("source"),
        "normalized_path": relpath(path),
        "openai_chat_completion": {"messages": compact_messages},
    }


def compact_content(content: Any, *, keep_full: bool) -> Any:
    if not isinstance(content, str):
        return content
    if keep_full or len(content) <= 12000:
        return content
    head = content[:8000]
    tail = content[-3000:]
    return head + "\n\n[...TRUNCATED OVERSIZED ENVIRONMENT OUTPUT...]\n\n" + tail


def render_payload(args: argparse.Namespace, payload: Any) -> int:
    if args.pass_name == "synthesize-skill" and isinstance(payload, dict) and payload.get("skip"):
        print(f"skip synthesize-skill: {payload.get('reason', '').strip()}")
        return 0
    if args.pass_name == "consolidate-guidelines":
        clusters = payload.get("clusters") if isinstance(payload, dict) else None
        if not clusters:
            print("skip consolidate-guidelines: no clusters")
            return 0
        for cluster in clusters:
            run_render(args, cluster)
        return 0
    if args.pass_name == "extract-guidelines" and payload == {"entities": []}:
        print("skip extract-guidelines: no entities")
        return 0
    return run_render(args, payload)


def run_render(args: argparse.Namespace, payload: Any) -> int:
    cmd = [
        sys.executable,
        str(BUILD_SCRIPT),
        "--wiki-root",
        str(args.wiki_root),
        PASS_TO_RENDER_CMD[args.pass_name],
    ]
    if args.rewrite:
        cmd.append("--rewrite")
    if args.pass_name == "synthesize-skill" and args.archive_covered:
        cmd.append("--archive-covered")
    result = subprocess.run(cmd, input=json.dumps(payload), text=True)
    return result.returncode


def relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
