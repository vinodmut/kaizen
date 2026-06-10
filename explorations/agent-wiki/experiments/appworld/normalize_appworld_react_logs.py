#!/usr/bin/env python3
"""Normalize AppWorld ReAct experiment logs into agent-wiki trajectory JSON.

Use this on fresh AppWorld train runs with `log_lm_calls=true`. The public
downloaded AppWorld outputs often omit `lm_calls.jsonl` and `logger.jsonl`, so
they are useful for evaluation but not enough for high-quality wiki extraction.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--appworld-root",
        type=Path,
        default=Path(os.environ.get("APPWORLD_ROOT", "benchmark-data/appworld")),
    )
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--task-id", action="append", default=[])
    parser.add_argument("--task-ids-file", type=Path, default=None)
    parser.add_argument("--manifest-split", default="train")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--allow-empty", action="store_true", help="Write files even when no messages were found.")
    parser.add_argument(
        "--keep-prompt-examples",
        action="store_true",
        help="Keep AppWorld few-shot prompt examples in the normalized message list.",
    )
    args = parser.parse_args()

    experiment_dir = args.appworld_root / "experiments" / "outputs" / args.experiment_name
    task_ids = args.task_id or load_task_ids(args.task_ids_file, args.manifest_split)
    if not task_ids:
        tasks_dir = experiment_dir / "tasks"
        task_ids = sorted(path.name for path in tasks_dir.iterdir() if path.is_dir())

    evaluations = load_evaluation_individuals(experiment_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    skipped = []
    for task_id in task_ids:
        normalized = normalize_task(
            experiment_dir,
            args.experiment_name,
            task_id,
            evaluations.get(task_id, {}),
            drop_prompt_examples=not args.keep_prompt_examples,
        )
        if not normalized["openai_chat_completion"]["messages"] and not args.allow_empty:
            skipped.append({"task_id": task_id, "reason": "no lm_calls.jsonl or logger.jsonl messages"})
            continue
        out_path = args.out_dir / f"{safe_filename(task_id)}.json"
        out_path.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
        written.append(str(out_path))

    summary = {
        "experiment_name": args.experiment_name,
        "appworld_root": str(args.appworld_root),
        "out_dir": str(args.out_dir),
        "written_count": len(written),
        "skipped_count": len(skipped),
        "written": written,
        "skipped": skipped,
    }
    summary_path = args.out_dir.parent / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(written)} normalized trajectories to {args.out_dir}")
    if skipped:
        print(f"skipped {len(skipped)} task(s); see {summary_path}")
    return 0


def normalize_task(
    experiment_dir: Path,
    experiment_name: str,
    task_id: str,
    evaluation: dict[str, Any],
    drop_prompt_examples: bool,
) -> dict[str, Any]:
    task_dir = experiment_dir / "tasks" / task_id
    logs_dir = task_dir / "logs"
    lm_calls = list(iter_jsonl(logs_dir / "lm_calls.jsonl"))
    logger_events = list(iter_jsonl(logs_dir / "logger.jsonl"))
    api_calls = list(iter_jsonl(logs_dir / "api_calls.jsonl"))
    usage = load_json(task_dir / "misc" / "usage.json") or {}

    messages = messages_from_lm_calls(lm_calls)
    if not messages:
        messages = messages_from_logger(logger_events)
    append_trailing_environment(messages, logger_events)
    if drop_prompt_examples:
        messages = drop_appworld_prompt_examples(messages)

    session_id = f"appworld__{experiment_name}__{task_id}"
    model = infer_model(lm_calls)
    normalized = {
        "schema_version": "1",
        "dataset": "appworld",
        "agent": "appworld-react-code",
        "session_id": session_id,
        "metadata": {
            "id": session_id,
            "benchmark": "appworld",
            "experiment_name": experiment_name,
            "task_id": task_id,
        },
        "model": model,
        "models": [model] if model else [],
        "stats": {
            "message_count": len(messages),
            "assistant_turn_count": sum(1 for message in messages if message.get("role") == "assistant"),
            "environment_output_count": sum(
                1 for message in messages if message.get("role") == "user" and str(message.get("content", "")).startswith("Output:\n```")
            ),
            "lm_call_count": len(lm_calls),
            "api_call_count": len(api_calls),
            "top_tools": top_api_calls(api_calls),
            "input_tokens": get_nested_total(usage, ("tokens", "input_cache_miss"))
            + get_nested_total(usage, ("tokens", "input_cache_hit")),
            "output_tokens": get_nested_total(usage, ("tokens", "output")),
            "total_cost_usd": get_nested_total(usage, ("cost", "input_cache_miss"))
            + get_nested_total(usage, ("cost", "input_cache_hit"))
            + get_nested_total(usage, ("cost", "input_cache_write"))
            + get_nested_total(usage, ("cost", "output")),
        },
        "outcome": {
            "success": evaluation.get("success"),
            "difficulty": evaluation.get("difficulty"),
            "num_tests": evaluation.get("num_tests"),
            "passes": evaluation.get("passes", []),
            "failures": evaluation.get("failures", []),
        },
        "openai_chat_completion": {"messages": messages},
        "messages": messages,
        "usage": usage,
        "source": {
            "experiment_dir": str(experiment_dir),
            "task_dir": str(task_dir),
            "lm_calls_path": str(logs_dir / "lm_calls.jsonl"),
            "logger_path": str(logs_dir / "logger.jsonl"),
            "api_calls_path": str(logs_dir / "api_calls.jsonl"),
            "prompt_examples_dropped": drop_prompt_examples,
        },
    }
    return normalized


def messages_from_lm_calls(lm_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not lm_calls:
        return []
    last_call = lm_calls[-1]
    messages = [clean_message(message) for message in last_call.get("input", {}).get("messages", [])]
    final_message = first_choice_message(last_call.get("output", {}))
    if final_message and not same_message(messages[-1] if messages else {}, final_message):
        messages.append(clean_message(final_message))
    return messages


def messages_from_logger(logger_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for event in logger_events:
        role = event.get("role")
        content = event.get("content")
        if role == "agent":
            messages.append({"role": "assistant", "content": content or ""})
        elif role == "environment":
            messages.append({"role": "user", "content": wrap_environment_output(content or "")})
        elif role == "user":
            messages.append({"role": "user", "content": content or ""})
    return messages


def append_trailing_environment(messages: list[dict[str, Any]], logger_events: list[dict[str, Any]]) -> None:
    if not messages or not logger_events:
        return
    last_event = logger_events[-1]
    if last_event.get("role") != "environment":
        return
    wrapped = wrap_environment_output(last_event.get("content") or "")
    if not any(message.get("content") == wrapped for message in messages[-3:]):
        messages.append({"role": "user", "content": wrapped})


def drop_appworld_prompt_examples(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove AppWorld few-shot examples before the actual task.

    AppWorld's ReAct prompt is a role-tagged transcript with demo turns followed
    by key instructions and the real task. `lm_calls.jsonl` records the full
    prompt, but wiki extraction should not treat demo turns as trajectory
    evidence. Keep the key-instructions block when present, then the actual task
    and subsequent agent/environment turns.
    """
    actual_task_index = None
    for index, message in enumerate(messages):
        content = message.get("content")
        if not isinstance(content, str):
            continue
        if "Using these APIs, now generate code to solve the actual task:" in content:
            actual_task_index = index
    if actual_task_index is None:
        return messages

    start_index = actual_task_index
    for index in range(actual_task_index - 1, -1, -1):
        content = messages[index].get("content")
        if isinstance(content, str) and "**Key instructions**" in content:
            start_index = index
            break
    return messages[start_index:]


def first_choice_message(output: dict[str, Any]) -> dict[str, Any] | None:
    choices = output.get("choices") or []
    if not choices:
        return None
    message = choices[0].get("message")
    return message if isinstance(message, dict) else None


def clean_message(message: dict[str, Any]) -> dict[str, Any]:
    keep_keys = (
        "role",
        "content",
        "reasoning_content",
        "tool_calls",
        "function_call",
        "name",
        "tool_call_id",
    )
    return {key: value for key, value in message.items() if key in keep_keys and value is not None}


def same_message(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left.get("role") == right.get("role") and left.get("content") == right.get("content")


def wrap_environment_output(content: str) -> str:
    maybe_newline = "\n" if not content.endswith("\n") else ""
    return "Output:\n```\n" + content + maybe_newline + "```\n\n"


def infer_model(lm_calls: list[dict[str, Any]]) -> str:
    for call in lm_calls:
        model = call.get("input", {}).get("model")
        if model:
            return str(model)
    return "unknown"


def top_api_calls(api_calls: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for call in api_calls:
        data = call.get("data") or {}
        app_name = data.get("app_name")
        api_name = data.get("api_name")
        url = call.get("url", "")
        key = ".".join(part for part in (app_name, api_name) if part) or str(url)
        counter[key] += 1
    return [{"tool": key, "count": count} for key, count in counter.most_common(limit)]


def get_nested_total(data: dict[str, Any], keys: tuple[str, ...]) -> float:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return 0.0
        current = current.get(key)
    return float(current) if isinstance(current, int | float) else 0.0


def load_task_ids(path: Path | None, split: str) -> list[str]:
    if path is None:
        return []
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [str(item) for item in data]
    if isinstance(data, dict) and "task_ids" in data:
        return [str(item) for item in data["task_ids"]]
    if isinstance(data, dict) and isinstance(data.get(split), dict):
        return [str(item) for item in data[split]["task_ids"]]
    raise SystemExit(f"Could not read task ids for split {split!r} from {path}")


def load_evaluation_individuals(experiment_dir: Path) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    evaluations_dir = experiment_dir / "evaluations"
    if not evaluations_dir.exists():
        return output
    for path in sorted(evaluations_dir.glob("*.json")):
        data = load_json(path) or {}
        individuals = data.get("individual", {})
        if isinstance(individuals, dict):
            output.update(individuals)
    return output


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def iter_jsonl(path: Path) -> Any:
    if not path.exists():
        return
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def safe_filename(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)


if __name__ == "__main__":
    raise SystemExit(main())
