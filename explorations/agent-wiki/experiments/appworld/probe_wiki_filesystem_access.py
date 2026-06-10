#!/usr/bin/env python3
"""Probe whether AppWorld's Python REPL can read local agent-wiki files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Any AppWorld task id available locally.")
    parser.add_argument("--wiki-root", required=True, type=Path, help="Wiki root containing AGENTS.md.")
    parser.add_argument("--experiment-name", default="agent_wiki_probe")
    args = parser.parse_args()

    try:
        from appworld import AppWorld
    except ImportError as exc:
        raise SystemExit("AppWorld is required to probe wiki filesystem access.") from exc

    wiki_root = args.wiki_root.expanduser().resolve()
    agents_md = wiki_root / "AGENTS.md"
    if not agents_md.exists():
        raise SystemExit(f"{agents_md} does not exist")

    code = f"""
from pathlib import Path
wiki_root = Path({str(wiki_root)!r})
try:
    text = (wiki_root / "AGENTS.md").read_text(encoding="utf-8")
    print({{"ok": True, "path": str(wiki_root / "AGENTS.md"), "prefix": text[:200]}})
except Exception as exc:
    print({{"ok": False, "path": str(wiki_root / "AGENTS.md"), "error_type": type(exc).__name__, "error": str(exc)}})
"""

    with AppWorld(task_id=args.task_id, experiment_name=args.experiment_name) as world:
        outputs = world.batch_execute([code])

    print(json.dumps({"task_id": args.task_id, "wiki_root": str(wiki_root), "output": outputs[0]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
