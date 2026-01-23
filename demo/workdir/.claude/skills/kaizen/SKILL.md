---
name: kaizen
description: Get coding guidelines and best practices from Kaizen knowledge base. Use this when starting any coding task to follow established patterns.
argument-hint: [task description]
---

Retrieve guidelines from the Kaizen knowledge base for the current task.

## Usage

Run the script to fetch guidelines:

```bash
python3 .claude/skills/kaizen/get_guidelines.py "$ARGUMENTS"
```

If no arguments provided, describe the current task based on conversation context.

## Output

The script returns formatted guidelines from the Kaizen server. Review and apply these guidelines to your implementation.
