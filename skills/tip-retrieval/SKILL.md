---
name: tip-retrieval
description: Retrieves relevant tips from a knowledge base using LLM-based semantic matching. Designed to be invoked automatically via hooks to inject context-appropriate guidelines before task execution.
---

# Tip Retrieval

## Overview

This skill retrieves relevant tips from a stored knowledge base based on the current task context. It uses an LLM to semantically match the user's prompt against stored tips, returning only those that are relevant to the task at hand.

## Usage

### Automatic (via Hook)

Configure a `UserPromptSubmit` hook to invoke this skill automatically:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "command": "python3 /path/to/skills/tip-retrieval/scripts/retrieve_tips.py"
    }]
  }
}
```

The hook reads the user prompt from stdin and outputs relevant tips to stdout, which gets injected into the conversation context.

### Manual

```bash
echo '{"prompt": "help me debug this Python memory leak"}' | python3 scripts/retrieve_tips.py
```

## Configuration

### Tips Storage

Tips are stored in `.claude/tips.json` in the project root:

```json
{
  "tips": [
    {
      "content": "Use context managers for file operations",
      "rationale": "Ensures proper resource cleanup",
      "category": "strategy",
      "trigger": "When processing files or managing resources"
    }
  ]
}
```

### Environment Variables

- `ANTHROPIC_API_KEY`: Required for LLM-based retrieval
- `TIPS_FILE`: Optional path to tips JSON file (defaults to `.claude/tips.json`)
- `MAX_TIPS`: Maximum tips to return (defaults to 5)

## How It Works

1. Hook fires on user prompt submission
2. Script reads prompt from stdin (JSON with `prompt` field)
3. Loads all tips from the tips JSON file
4. Sends prompt + tips to LLM asking which are relevant
5. Outputs relevant tips to stdout
6. Claude receives tips as additional context

## Resources

### scripts/

**retrieve_tips.py**: Main retrieval script
- Reads hook input from stdin
- Uses Claude API for semantic matching
- Outputs relevant tips to stdout
