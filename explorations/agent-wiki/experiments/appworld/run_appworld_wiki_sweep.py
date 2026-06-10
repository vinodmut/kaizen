#!/usr/bin/env python3
"""Run baseline/wiki AppWorld arms over a slice manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_ARMS = ("baseline", "guidelines", "skills", "both", "pruned")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--task-ids-file", required=True, type=Path)
    parser.add_argument("--manifest-split", default="dev")
    parser.add_argument("--experiment-prefix", required=True)
    parser.add_argument("--arms", default=",".join(DEFAULT_ARMS))
    parser.add_argument(
        "--wiki-root",
        action="append",
        default=[],
        metavar="ARM=PATH",
        help="Wiki root for a non-baseline arm. Repeat for each wiki arm.",
    )
    parser.add_argument("--wiki-access-mode", choices=["direct_file", "prompt_index"], default="direct_file")
    parser.add_argument("--prompt-index-char-budget", type=int, default=12000)
    parser.add_argument("--num-processes", type=int, default=1)
    parser.add_argument("--process-index", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    script = Path(__file__).with_name("run_wiki_react_experiment.py")
    wiki_roots = parse_wiki_roots(args.wiki_root)
    arms = [arm.strip() for arm in args.arms.split(",") if arm.strip()]
    commands = []
    for arm in arms:
        command = [
            sys.executable,
            str(script),
            "--config",
            str(args.config),
            "--experiment-name",
            f"{args.experiment_prefix}_{arm}",
            "--task-ids-file",
            str(args.task_ids_file),
            "--manifest-split",
            args.manifest_split,
            "--arm",
            arm,
            "--num-processes",
            str(args.num_processes),
            "--process-index",
            str(args.process_index),
        ]
        if arm != "baseline":
            if arm not in wiki_roots:
                raise SystemExit(f"Missing --wiki-root {arm}=PATH")
            command.extend(
                [
                    "--wiki-root",
                    str(wiki_roots[arm]),
                    "--wiki-access-mode",
                    args.wiki_access_mode,
                    "--prompt-index-char-budget",
                    str(args.prompt_index_char_budget),
                ]
            )
        commands.append(command)

    print(json.dumps({"commands": commands}, indent=2))
    if args.dry_run:
        return 0
    for command in commands:
        subprocess.run(command, check=True)
    return 0


def parse_wiki_roots(values: list[str]) -> dict[str, Path]:
    output: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Expected ARM=PATH for --wiki-root, got {value!r}")
        arm, raw_path = value.split("=", 1)
        output[arm] = Path(raw_path).expanduser().resolve()
    return output


if __name__ == "__main__":
    raise SystemExit(main())
