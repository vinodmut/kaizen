#!/usr/bin/env python3
"""Evaluate an AppWorld experiment on a slice manifest.

AppWorld's CLI evaluates a full dataset or one task. This helper evaluates the
exact task ids in a slice manifest and writes a normal AppWorld-style
evaluations/<name>.json plus a text table.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--task-ids-file", required=True, type=Path)
    parser.add_argument("--manifest-split", required=True)
    parser.add_argument("--evaluation-name", default=None)
    parser.add_argument("--suppress-errors", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-details", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--save-reports", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        from appworld.common.io import write_file, write_json
        from appworld.common.path_store import path_store
        from appworld.common.printer import table_data_to_string
        from appworld.evaluator import Metric, evaluate_tasks
    except ImportError as exc:
        raise SystemExit("AppWorld is required to evaluate an AppWorld slice.") from exc

    task_ids = load_manifest_task_ids(args.task_ids_file, args.manifest_split)
    evaluation = evaluate_tasks(
        task_ids=task_ids,
        experiment_name=args.experiment_name,
        suppress_errors=args.suppress_errors,
        include_details=args.include_details,
        save_reports=args.save_reports,
    )

    evaluation_name = args.evaluation_name or f"{args.manifest_split}_slice"
    evaluations_dir = Path(path_store.experiment_outputs) / args.experiment_name / "evaluations"
    evaluations_dir.mkdir(parents=True, exist_ok=True)
    json_path = evaluations_dir / f"{evaluation_name}.json"
    txt_path = evaluations_dir / f"{evaluation_name}.txt"
    write_json(evaluation, str(json_path), silent=True)
    table = table_data_to_string(Metric.build_report(evaluation))
    write_file(table, str(txt_path))
    print(f"wrote {json_path}")
    print(f"wrote {txt_path}")
    return 0


def load_manifest_task_ids(path: Path, split: str) -> list[str]:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [str(item) for item in data]
    if isinstance(data, dict) and "task_ids" in data:
        return [str(item) for item in data["task_ids"]]
    if not isinstance(data, dict):
        raise SystemExit(f"Unsupported manifest shape: {path}")
    split_data = data.get(split)
    if not isinstance(split_data, dict) or "task_ids" not in split_data:
        raise SystemExit(f"Manifest {path} has no {split}.task_ids list")
    return [str(item) for item in split_data["task_ids"]]


if __name__ == "__main__":
    raise SystemExit(main())
