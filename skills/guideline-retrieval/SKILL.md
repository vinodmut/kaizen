---
name: guideline-retrieval
description: Retrieves relevant guidelines from a knowledge base using LLM-based semantic matching. Designed to be invoked automatically via hooks to inject context-appropriate guidelines before task execution.
---

# Guideline Retrieval

## Overview

This skill retrieves relevant guidelines from a stored knowledge base based on the current task context. It uses an LLM to semantically match the user's prompt against stored guidelines, returning only those that are relevant to the task at hand.

## Usage

### Automatic (via Hook)

Configure a `UserPromptSubmit` hook to invoke this skill automatically:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "command": "python3 /path/to/skills/guideline-retrieval/scripts/retrieve_guidelines.py"
    }]
  }
}
```

The hook reads the user prompt from stdin and outputs relevant guidelines to stdout, which gets injected into the conversation context.

### Manual

```bash
echo '{"prompt": "help me debug this Python memory leak"}' | python3 scripts/retrieve_guidelines.py
```

## Configuration

### Guidelines Storage

Guidelines are stored in `.claude/guidelines.json` in the project root:

```json
{
  "guidelines": [
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
- `GUIDELINES_FILE`: Optional path to guidelines JSON file (defaults to `.claude/guidelines.json`)
- `MAX_GUIDELINES`: Maximum guidelines to return (defaults to 5)

## How It Works

1. Hook fires on user prompt submission
2. Script reads prompt from stdin (JSON with `prompt` field)
3. Loads all guidelines from the guidelines JSON file
4. Sends prompt + guidelines to LLM asking which are relevant
5. Outputs relevant guidelines to stdout
6. Claude receives guidelines as additional context

## Resources

### scripts/

**retrieve_guidelines.py**: Main retrieval script
- Reads hook input from stdin
- Uses Claude API for semantic matching
- Outputs relevant guidelines to stdout
