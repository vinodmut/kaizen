#!/usr/bin/env python3
"""
Tip Retrieval Script
Uses LLM to retrieve relevant tips based on user prompt.
"""

import json
import os
import sys
from pathlib import Path


def find_tips_file():
    """Find tips.json file, checking multiple locations."""
    locations = [
        os.environ.get("TIPS_FILE"),
        ".claude/tips.json",
        Path(__file__).parent.parent.parent.parent / "tips.json",
    ]

    for loc in locations:
        if loc and Path(loc).exists():
            return Path(loc)

    return None


def load_tips(tips_path):
    """Load tips from JSON file."""
    with open(tips_path) as f:
        data = json.load(f)
    return data.get("tips", [])


def retrieve_relevant_tips(prompt, tips, max_tips=5):
    """Use LLM to find tips relevant to the prompt."""
    if not tips:
        return []

    try:
        import anthropic
    except ImportError:
        print("Installing anthropic...", file=sys.stderr)
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", "anthropic"],
            stderr=subprocess.DEVNULL
        )
        import anthropic

    client = anthropic.Anthropic()

    # Format tips for the prompt
    tips_text = "\n".join(
        f"{i+1}. [{tip.get('category', 'general')}] {tip['content']} (Trigger: {tip.get('trigger', 'any')})"
        for i, tip in enumerate(tips)
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": f"""Given this user task:
"{prompt}"

Which of these tips are relevant? Return ONLY the numbers of relevant tips as a comma-separated list, or "none" if none apply.

Tips:
{tips_text}

Relevant tip numbers:"""
        }]
    )

    result = response.content[0].text.strip().lower()

    if result == "none" or not result:
        return []

    # Parse tip numbers
    try:
        indices = [int(n.strip()) - 1 for n in result.replace(",", " ").split() if n.strip().isdigit()]
        return [tips[i] for i in indices if 0 <= i < len(tips)][:max_tips]
    except (ValueError, IndexError):
        return []


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = hook_input.get("prompt", "")
    if not prompt:
        sys.exit(0)

    # Find and load tips
    tips_path = find_tips_file()
    if not tips_path:
        sys.exit(0)

    tips = load_tips(tips_path)
    if not tips:
        sys.exit(0)

    # Retrieve relevant tips
    max_tips = int(os.environ.get("MAX_TIPS", 5))
    relevant = retrieve_relevant_tips(prompt, tips, max_tips)

    # Output to stdout (gets injected into context)
    if relevant:
        print("\n## Guidelines for this task\n")
        for tip in relevant:
            category = tip.get("category", "tip")
            print(f"- **[{category}]** {tip['content']}")
            if tip.get("rationale"):
                print(f"  - _{tip['rationale']}_")
        print()


if __name__ == "__main__":
    main()
