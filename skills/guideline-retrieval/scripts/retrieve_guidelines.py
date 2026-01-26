#!/usr/bin/env python3
"""Retrieve and output guidelines for Claude to filter."""

import json
import os
import sys
from pathlib import Path


def find_guidelines_file():
    """Find the guidelines file in common locations."""
    locations = [
        os.environ.get("GUIDELINES_FILE"),
        ".claude/guidelines.json",
        Path(__file__).parent.parent.parent.parent / "guidelines.json",
    ]
    for loc in locations:
        if loc and Path(loc).exists():
            return Path(loc)
    return None


def load_guidelines():
    """Load guidelines from the guidelines file."""
    guidelines_file = find_guidelines_file()
    if not guidelines_file:
        return []
    try:
        with open(guidelines_file) as f:
            data = json.load(f)
        return data.get("guidelines", [])
    except (json.JSONDecodeError, IOError):
        return []


def format_guidelines(guidelines):
    """Format all guidelines for Claude to review."""
    header = """## Guidelines for this task

Review these guidelines and apply any relevant ones:

"""
    items = []
    for g in guidelines:
        item = f"- **[{g.get('category', 'general')}]** {g['content']}"
        if g.get('rationale'):
            item += f"\n  - _Rationale: {g['rationale']}_"
        if g.get('trigger'):
            item += f"\n  - _When: {g['trigger']}_"
        items.append(item)

    return header + "\n".join(items)


def main():
    # Read input from stdin (hook provides JSON with prompt)
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    # Load all guidelines
    guidelines = load_guidelines()
    if not guidelines:
        return

    # Output all guidelines - Claude will filter for relevance
    print(format_guidelines(guidelines))


if __name__ == "__main__":
    main()
