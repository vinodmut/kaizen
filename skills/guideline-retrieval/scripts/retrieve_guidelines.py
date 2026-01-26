#!/usr/bin/env python3
"""
Guideline Retrieval Script
Uses LLM to retrieve relevant guidelines based on user prompt.
"""

import json
import os
import sys
from pathlib import Path


def find_guidelines_file():
    """Find guidelines.json file, checking multiple locations."""
    locations = [
        os.environ.get("GUIDELINES_FILE"),
        ".claude/guidelines.json",
        Path(__file__).parent.parent.parent.parent / "guidelines.json",
    ]

    for loc in locations:
        if loc and Path(loc).exists():
            return Path(loc)

    return None


def load_guidelines(guidelines_path):
    """Load guidelines from JSON file."""
    with open(guidelines_path) as f:
        data = json.load(f)
    return data.get("guidelines", [])


def retrieve_relevant_guidelines(prompt, guidelines, max_guidelines=5):
    """Use LLM to find guidelines relevant to the prompt."""
    if not guidelines:
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

    # Format guidelines for the prompt
    guidelines_text = "\n".join(
        f"{i+1}. [{guideline.get('category', 'general')}] {guideline['content']} (Trigger: {guideline.get('trigger', 'any')})"
        for i, guideline in enumerate(guidelines)
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": f"""Given this user task:
"{prompt}"

Which of these guidelines are relevant? Return ONLY the numbers of relevant guidelines as a comma-separated list, or "none" if none apply.

Guidelines:
{guidelines_text}

Relevant guideline numbers:"""
        }]
    )

    result = response.content[0].text.strip().lower()

    if result == "none" or not result:
        return []

    # Parse guideline numbers
    try:
        indices = [int(n.strip()) - 1 for n in result.replace(",", " ").split() if n.strip().isdigit()]
        return [guidelines[i] for i in indices if 0 <= i < len(guidelines)][:max_guidelines]
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

    # Find and load guidelines
    guidelines_path = find_guidelines_file()
    if not guidelines_path:
        sys.exit(0)

    guidelines = load_guidelines(guidelines_path)
    if not guidelines:
        sys.exit(0)

    # Retrieve relevant guidelines
    max_guidelines = int(os.environ.get("MAX_GUIDELINES", 5))
    relevant = retrieve_relevant_guidelines(prompt, guidelines, max_guidelines)

    # Output to stdout (gets injected into context)
    if relevant:
        print("\n## Guidelines for this task\n")
        for guideline in relevant:
            category = guideline.get("category", "guideline")
            print(f"- **[{category}]** {guideline['content']}")
            if guideline.get("rationale"):
                print(f"  - _{guideline['rationale']}_")
        print()


if __name__ == "__main__":
    main()
