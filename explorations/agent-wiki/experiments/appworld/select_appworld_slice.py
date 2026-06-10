#!/usr/bin/env python3
"""Select a small strict AppWorld train/dev slice manifest."""

from __future__ import annotations

import argparse
import datetime
import json
import random
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-count", type=int, default=20)
    parser.add_argument("--dev-count", type=int, default=20)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    try:
        from appworld.task import load_task_ids
    except ImportError as exc:
        raise SystemExit("AppWorld is required to select AppWorld task ids.") from exc

    rng = random.Random(args.seed)
    train_ids = sorted(load_task_ids("train"))
    dev_ids = sorted(load_task_ids("dev"))
    if args.train_count > len(train_ids):
        raise SystemExit(f"train-count {args.train_count} exceeds available train tasks {len(train_ids)}")
    if args.dev_count > len(dev_ids):
        raise SystemExit(f"dev-count {args.dev_count} exceeds available dev tasks {len(dev_ids)}")

    train_sample = sorted(rng.sample(train_ids, args.train_count))
    dev_sample = sorted(rng.sample(dev_ids, args.dev_count))
    manifest = {
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "seed": args.seed,
        "strict_split": True,
        "train": {
            "dataset": "train",
            "count": len(train_sample),
            "task_ids": train_sample,
        },
        "dev": {
            "dataset": "dev",
            "count": len(dev_sample),
            "task_ids": dev_sample,
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
