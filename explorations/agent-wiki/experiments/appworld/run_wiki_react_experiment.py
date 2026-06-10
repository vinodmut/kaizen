#!/usr/bin/env python3
"""Run AppWorld's ReAct agent with optional agent-wiki injection.

This script imports `agent_wiki_react_code_agent`, which registers a new
AppWorld simplified agent type, then delegates execution to AppWorld's normal
`run_experiment` helper.
"""

from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path, help="AppWorld experiment config JSON or Jsonnet.")
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--task-id", default=None, help="Optional single task id. Omit to run config dataset.")
    parser.add_argument(
        "--task-ids-file",
        type=Path,
        default=None,
        help="Optional JSON manifest containing task_ids or train/dev task_ids.",
    )
    parser.add_argument(
        "--manifest-split",
        choices=["train", "dev", "test_normal", "test_challenge"],
        default=None,
        help="Split key to read from --task-ids-file when it is a slice manifest.",
    )
    parser.add_argument("--arm", required=True, choices=["baseline", "guidelines", "skills", "both", "pruned"])
    parser.add_argument("--wiki-root", type=Path, default=None, help="Required for non-baseline arms.")
    parser.add_argument("--wiki-access-mode", choices=["direct_file", "prompt_index"], default="direct_file")
    parser.add_argument("--prompt-index-char-budget", type=int, default=12000)
    parser.add_argument("--num-processes", type=int, default=1)
    parser.add_argument("--process-index", type=int, default=0)
    args = parser.parse_args()

    if args.task_id and args.task_ids_file:
        raise SystemExit("Only one of --task-id or --task-ids-file may be set.")

    config = load_config(args.config)
    task_ids = load_task_ids_file(args.task_ids_file, args.manifest_split)
    if args.task_id:
        task_ids = [args.task_id]
    if task_ids is None:
        run_one(args.experiment_name, config, args, task_id=None)
        return 0

    selected_task_ids = shard_task_ids(task_ids, args.num_processes, args.process_index)
    for task_id in selected_task_ids:
        run_one(args.experiment_name, config, args, task_id=task_id)
    return 0


def run_one(experiment_name: str, config: dict[str, Any], args: argparse.Namespace, task_id: str | None) -> None:
    runner_config = build_runner_config(config, args)
    run_experiment = import_appworld_runner()
    run_experiment(
        experiment_name=experiment_name,
        runner_config=runner_config,
        task_id=task_id,
        num_processes=1 if task_id else args.num_processes,
        process_index=0 if task_id else args.process_index,
    )


def import_appworld_runner() -> Any:
    try:
        # Import for side effect: registers `agent_wiki_react_code_agent`.
        import agent_wiki_react_code_agent  # noqa: F401
        from appworld_agents.code.simplified.run import run_experiment
    except ImportError as exc:
        raise SystemExit("AppWorld and appworld_agents are required to run this experiment.") from exc
    return run_experiment


def build_runner_config(config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    runner_config = config.get("config", config)
    runner_config = deepcopy(runner_config)
    agent_config = runner_config["agent"]

    if args.arm == "baseline":
        if args.wiki_root is not None:
            raise SystemExit("--wiki-root should not be set for baseline")
        return runner_config

    if args.wiki_root is None:
        raise SystemExit("--wiki-root is required for non-baseline arms")
    agent_config["type"] = "agent_wiki_react_code_agent"
    agent_config["wiki_root"] = str(args.wiki_root.expanduser().resolve())
    agent_config["wiki_arm"] = args.arm
    agent_config["wiki_access_mode"] = args.wiki_access_mode
    agent_config["prompt_index_char_budget"] = args.prompt_index_char_budget
    return runner_config


def load_config(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if suffix == ".jsonnet":
        try:
            import _jsonnet  # type: ignore[import-not-found]
        except ImportError as exc:
            raise SystemExit("Jsonnet config support requires the _jsonnet package.") from exc
        ext_vars = appworld_jsonnet_ext_vars()
        rendered = _jsonnet.evaluate_file(str(path), ext_vars=ext_vars)
        return json.loads(rendered)
    raise SystemExit(f"Unsupported config type: {path}")


def appworld_jsonnet_ext_vars() -> dict[str, str]:
    try:
        from appworld.common.path_store import path_store
    except ImportError:
        defaults = {
            "APPWORLD_EXPERIMENT_PROMPTS_PATH": "",
            "APPWORLD_EXPERIMENT_CONFIGS_PATH": "",
            "APPWORLD_EXPERIMENT_CODE_PATH": "",
        }
    else:
        defaults = {
            "APPWORLD_EXPERIMENT_PROMPTS_PATH": path_store.experiment_prompts,
            "APPWORLD_EXPERIMENT_CONFIGS_PATH": path_store.experiment_configs,
            "APPWORLD_EXPERIMENT_CODE_PATH": path_store.experiment_code,
        }
    return {key: os.environ.get(key, default) for key, default in defaults.items()}


def load_task_ids_file(path: Path | None, split: str | None) -> list[str] | None:
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [str(item) for item in data]
    if not isinstance(data, dict):
        raise SystemExit(f"Unsupported task id manifest shape in {path}")
    if "task_ids" in data:
        return [str(item) for item in data["task_ids"]]
    if split is None:
        split_keys = [key for key in ("train", "dev", "test_normal", "test_challenge") if key in data]
        if len(split_keys) != 1:
            raise SystemExit(f"--manifest-split is required for manifest {path}")
        split = split_keys[0]
    split_data = data.get(split)
    if not isinstance(split_data, dict) or "task_ids" not in split_data:
        raise SystemExit(f"Manifest {path} has no {split}.task_ids list")
    return [str(item) for item in split_data["task_ids"]]


def shard_task_ids(task_ids: list[str], num_processes: int, process_index: int) -> list[str]:
    if num_processes < 1:
        raise SystemExit("--num-processes must be >= 1")
    if process_index < 0 or process_index >= num_processes:
        raise SystemExit("--process-index must satisfy 0 <= process-index < num-processes")
    return [task_id for index, task_id in enumerate(task_ids) if index % num_processes == process_index]


if __name__ == "__main__":
    raise SystemExit(main())
