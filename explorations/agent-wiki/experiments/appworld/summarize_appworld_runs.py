#!/usr/bin/env python3
"""Summarize AppWorld agent-wiki experiment runs."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RunSpec:
    arm: str
    experiment_name: str


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--appworld-root",
        type=Path,
        default=Path(os.environ.get("APPWORLD_ROOT", "benchmark-data/appworld")),
    )
    parser.add_argument("--run", action="append", required=True, metavar="ARM=EXPERIMENT")
    parser.add_argument("--task-ids-file", type=Path, default=None)
    parser.add_argument("--manifest-split", default="dev")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    args = parser.parse_args()

    task_ids = load_task_ids(args.task_ids_file, args.manifest_split)
    rows = [summarize_run(args.appworld_root, parse_run_spec(run_spec), task_ids) for run_spec in args.run]
    summary = {"appworld_root": str(args.appworld_root), "runs": rows}
    print(render_markdown(rows))
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(rows) + "\n", encoding="utf-8")
    return 0


def summarize_run(appworld_root: Path, run_spec: RunSpec, task_ids: list[str] | None) -> dict[str, Any]:
    experiment_dir = appworld_root / "experiments" / "outputs" / run_spec.experiment_name
    tasks_dir = experiment_dir / "tasks"
    if not tasks_dir.exists():
        return {
            "arm": run_spec.arm,
            "experiment_name": run_spec.experiment_name,
            "error": f"missing {tasks_dir}",
        }
    discovered_task_ids = sorted(path.name for path in tasks_dir.iterdir() if path.is_dir())
    selected_task_ids = task_ids or discovered_task_ids
    evaluation = load_evaluation_individuals(experiment_dir)

    task_rows = []
    for task_id in selected_task_ids:
        task_dir = tasks_dir / task_id
        usage = load_json(task_dir / "misc" / "usage.json") or {}
        eval_row = evaluation.get(task_id, {})
        task_rows.append(
            {
                "task_id": task_id,
                "present": task_dir.exists(),
                "success": eval_row.get("success"),
                "difficulty": eval_row.get("difficulty"),
                "num_tests": eval_row.get("num_tests"),
                "steps": count_logger_role(task_dir / "logs" / "logger.jsonl", "agent"),
                "api_calls": count_lines(task_dir / "logs" / "api_calls.jsonl"),
                "wiki_access_signals": count_wiki_access_signals(task_dir / "logs" / "logger.jsonl"),
                "usage": usage,
            }
        )

    present = [row for row in task_rows if row["present"]]
    known_success = [row for row in present if row["success"] is not None]
    successes = sum(1 for row in known_success if row["success"])
    totals = usage_totals(present)
    total_steps = sum(row["steps"] or 0 for row in present)
    total_api_calls = sum(row["api_calls"] or 0 for row in present)
    wiki_tasks = sum(1 for row in present if (row["wiki_access_signals"] or 0) > 0)
    return {
        "arm": run_spec.arm,
        "experiment_name": run_spec.experiment_name,
        "tasks_requested": len(selected_task_ids),
        "tasks_present": len(present),
        "tasks_evaluated": len(known_success),
        "successes": successes,
        "success_rate": round(successes / len(known_success), 4) if known_success else None,
        "total_steps": total_steps,
        "avg_steps": round(total_steps / len(present), 2) if present else None,
        "total_api_calls": total_api_calls,
        "avg_api_calls": round(total_api_calls / len(present), 2) if present else None,
        "wiki_access_tasks": wiki_tasks,
        "usage": totals,
        "tasks": task_rows,
    }


def load_task_ids(path: Path | None, split: str) -> list[str] | None:
    if path is None:
        return None
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [str(item) for item in data]
    if isinstance(data, dict) and "task_ids" in data:
        return [str(item) for item in data["task_ids"]]
    if isinstance(data, dict) and isinstance(data.get(split), dict):
        return [str(item) for item in data[split]["task_ids"]]
    raise SystemExit(f"Could not read task ids for split {split!r} from {path}")


def parse_run_spec(value: str) -> RunSpec:
    if "=" not in value:
        raise SystemExit(f"Expected ARM=EXPERIMENT for --run, got {value!r}")
    arm, experiment_name = value.split("=", 1)
    return RunSpec(arm=arm, experiment_name=experiment_name)


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


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


def count_lines(path: Path) -> int | None:
    if not path.exists():
        return None
    return sum(1 for _ in path.open(encoding="utf-8"))


def count_logger_role(path: Path, role: str) -> int | None:
    if not path.exists():
        return None
    count = 0
    for event in iter_jsonl(path):
        if event.get("role") == role:
            count += 1
    return count


def count_wiki_access_signals(path: Path) -> int | None:
    if not path.exists():
        return None
    needles = ("AGENTS.md", "_index.jsonl", "agent-wiki", "agent_wiki", "wiki_root")
    count = 0
    for event in iter_jsonl(path):
        if event.get("role") == "user":
            continue
        content = event.get("content") or ""
        if any(needle in content for needle in needles):
            count += 1
    return count


def iter_jsonl(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def usage_totals(task_rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = {"tokens": {}, "cost": {}}
    for row in task_rows:
        usage = row.get("usage") or {}
        for section in ("tokens", "cost"):
            values = usage.get(section) or {}
            for key, value in values.items():
                if isinstance(value, int | float):
                    totals[section][key] = round(totals[section].get(key, 0.0) + value, 10)
    for section in totals.values():
        section["total"] = round(sum(section.values()), 10)
    return totals


def render_markdown(rows: list[dict[str, Any]]) -> str:
    headers = [
        "arm",
        "experiment",
        "present",
        "eval",
        "success",
        "cost",
        "tokens",
        "steps",
        "api_calls",
        "wiki_tasks",
    ]
    body = [headers]
    for row in rows:
        if "error" in row:
            body.append(
                [
                    row["arm"],
                    row["experiment_name"],
                    row["error"],
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            continue
        usage = row["usage"]
        body.append(
            [
                row["arm"],
                row["experiment_name"],
                str(row["tasks_present"]),
                str(row["tasks_evaluated"]),
                format_rate(row["success_rate"]),
                format_number(usage["cost"].get("total")),
                format_number(usage["tokens"].get("total"), digits=0),
                format_number(row["avg_steps"]),
                format_number(row["avg_api_calls"]),
                str(row["wiki_access_tasks"]),
            ]
        )
    widths = [max(len(str(item)) for item in column) for column in zip(*body, strict=True)]
    lines = ["# AppWorld Agent-Wiki Run Summary", ""]
    for index, row in enumerate(body):
        line = "  ".join(str(item).ljust(widths[col]) for col, item in enumerate(row))
        lines.append(line)
        if index == 0:
            lines.append("  ".join("-" * width for width in widths))
    return "\n".join(lines)


def format_rate(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def format_number(value: float | int | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    if digits == 0:
        return f"{value:.0f}"
    return f"{value:.{digits}f}"


if __name__ == "__main__":
    raise SystemExit(main())
