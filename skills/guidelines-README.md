# Guidelines Skills

Two complementary skills for extracting and retrieving actionable guidelines from conversations.

## Overview

| Skill | Purpose | Hook Type |
|-------|---------|-----------|
| `guideline-generator` | Extract guidelines from completed conversations | Stop |
| `guideline-retrieval` | Inject relevant guidelines before task execution | UserPromptSubmit |

---

## guideline-generator

Analyzes conversation trajectories to extract actionable guidelines. Transforms reactive learnings (what failed) into proactive recommendations (what to do first).

### Usage

Invoke the skill manually or configure a Stop hook to run automatically at conversation end.

**Manual invocation:**
```
/guideline-generator
```

**Output format:**
```json
{
  "guidelines": [
    {
      "content": "Use Python PIL/Pillow for image metadata extraction in sandboxed environments",
      "rationale": "System tools like exiftool may not be available; PIL is always installable via pip",
      "category": "strategy",
      "trigger": "When extracting image metadata in containerized or sandboxed environments"
    }
  ]
}
```

### Saving Guidelines

After generating guidelines, save them using the script:

```bash
echo '<guidelines_json>' | python3 scripts/save_guidelines.py
```

The script will:
- Find an existing guidelines file or create `.claude/guidelines.json`
- Append new guidelines (skipping duplicates by content)
- Print the actual storage path and count

### Guideline Categories

- **strategy**: High-level approach or methodology choices
- **recovery**: Handling errors, edge cases, or unexpected situations
- **optimization**: Improving efficiency, performance, or code quality

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GUIDELINES_FILE` | Path to guidelines JSON file | `.claude/guidelines.json` |

### Hook Configuration

Add to `.claude/settings.json` to auto-generate guidelines when conversations end:

```json
{
  "hooks": {
    "Stop": [
      {
        "command": "python3 /path/to/skills/guideline-generator/scripts/save_guidelines.py"
      }
    ]
  }
}
```

---

## guideline-retrieval

Outputs all guidelines for Claude to filter and apply. Injects context-appropriate guidelines before task execution without requiring a separate API key.

### Usage

**Automatic (recommended):** Configure a UserPromptSubmit hook to inject guidelines automatically.

**Manual:**
```bash
echo '{"prompt": "help me debug this Python memory leak"}' | python3 scripts/retrieve_guidelines.py
```

### Guidelines Storage

Store guidelines in `.claude/guidelines.json`:

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

| Variable | Description | Default |
|----------|-------------|---------|
| `GUIDELINES_FILE` | Path to guidelines JSON file | `.claude/guidelines.json` |

### Hook Configuration

Add to `.claude/settings.json` to inject guidelines on every prompt:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "command": "python3 /path/to/skills/guideline-retrieval/scripts/retrieve_guidelines.py"
      }
    ]
  }
}
```

### How It Works

1. Hook fires when user submits a prompt
2. Script reads prompt from stdin (JSON with `prompt` field)
3. Loads all guidelines from the guidelines file
4. Outputs all guidelines to stdout in a formatted list
5. Claude receives guidelines as additional context and filters for relevance

---

## Complete Setup

To use both skills together:

### 1. Create guidelines storage

```bash
mkdir -p .claude
echo '{"guidelines": []}' > .claude/guidelines.json
```

### 2. Configure hooks

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "command": "python3 /path/to/skills/guideline-retrieval/scripts/retrieve_guidelines.py"
      }
    ],
    "Stop": [
      {
        "command": "python3 /path/to/skills/guideline-generator/scripts/save_guidelines.py"
      }
    ]
  }
}
```

---

## Guideline Schema

All guidelines follow this structure:

| Field | Required | Description |
|-------|----------|-------------|
| `content` | Yes | The actionable guideline (max 200 chars) |
| `rationale` | No | Why this approach works (max 300 chars) |
| `category` | Yes | One of: `strategy`, `recovery`, `optimization` |
| `trigger` | Yes | Situational context when this applies (max 150 chars) |

### Writing Good Guidelines

**Proactive, not reactive:**
- Bad: "If npm install fails, try yarn instead"
- Good: "Use the package manager already configured in the project (check for yarn.lock vs package-lock.json)"

**Context-based triggers, not failure conditions:**
- Bad trigger: "When exiftool command fails"
- Good trigger: "When extracting image metadata in containerized or sandboxed environments"
