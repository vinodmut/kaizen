---
name: guideline-generator
description: Extract actionable guidelines from conversation trajectories. Analyzes user requests, steps taken, successes and failures to generate proactive guidelines that help on similar future tasks.
---

# Guideline Generator

## Overview

This skill analyzes conversation trajectories to extract actionable guidelines that would help on similar tasks in the future. It transforms reactive learnings (what failed) into proactive recommendations (what to do first).

## Hook Integration

This skill is designed to be triggered automatically via a **Stop hook** at the end of conversations:

```json
{
  "hooks": {
    "Stop": [{
      "command": "python3 /path/to/guideline-generator/scripts/save_guidelines.py"
    }]
  }
}
```

The Stop hook receives conversation context and can extract guidelines to append to the knowledge base.

## Workflow

### Step 1: Analyze the Conversation

Identify from your current conversation:

- **Task/Request**: What was the user asking for?
- **Steps Taken**: What reasoning, actions, and observations occurred?
- **What Worked**: Which approaches succeeded?
- **What Failed**: Which approaches didn't work and why?

### Step 2: Extract Guidelines

Extract 3-5 proactive guidelines following these principles:

1. **Reframe failures as proactive recommendations:**
   - If an approach failed due to permissions → recommend the alternative FIRST
   - If a system tool wasn't available → recommend what worked instead
   - If an approach hit environment constraints → recommend the constraint-aware approach

2. **Focus on what worked, stated as the primary approach:**
   - Bad: "If exiftool fails, use PIL instead"
   - Good: "In sandboxed environments, use Python libraries (PIL/Pillow) for image metadata extraction"

3. **Triggers should be situational context, not failure conditions:**
   - Bad trigger: "When apt-get fails"
   - Good trigger: "When working in containerized/sandboxed environments"

### Step 3: Output Guidelines JSON

Output guidelines in the following JSON format:

```json
{
  "guidelines": [
    {
      "content": "Proactive guideline stating what TO DO",
      "rationale": "Why this approach works better",
      "category": "strategy|recovery|optimization",
      "trigger": "Situational context when this applies"
    }
  ]
}
```

## Guideline Categories

- **strategy**: High-level approach or methodology choices
- **recovery**: Handling errors, edge cases, or unexpected situations
- **optimization**: Improving efficiency, performance, or code quality

## Examples

### Good vs Bad Guidelines

**BAD (reactive):**
```json
{
  "content": "Fall back to Python PIL when exiftool is not available",
  "trigger": "When exiftool command fails"
}
```

**GOOD (proactive):**
```json
{
  "content": "Use Python PIL/Pillow for image metadata extraction in sandboxed environments",
  "rationale": "System tools like exiftool may not be available; PIL is always installable via pip",
  "category": "strategy",
  "trigger": "When extracting image metadata in containerized or sandboxed environments"
}
```

### More Examples

**BAD:**
```json
{
  "content": "If npm install fails, try yarn instead",
  "trigger": "When npm throws errors"
}
```

**GOOD:**
```json
{
  "content": "Use the package manager already configured in the project (check for yarn.lock vs package-lock.json)",
  "rationale": "Mixing package managers causes dependency resolution conflicts",
  "category": "strategy",
  "trigger": "When installing dependencies in an existing project"
}
```

## Resources

### scripts/

**save_guidelines.py**: Saves generated guidelines to the guidelines file
- Reads JSON with `guidelines` array from stdin
- Finds existing file or creates new one at `.claude/guidelines.json`
- Appends new guidelines (deduplicates by content)
- Prints the actual storage path

### references/

**guideline_schema.md**: Complete JSON schema reference for guideline structure

**guideline_examples.md**: Extended collection of good vs bad guideline examples across different scenarios

## Integration

Guidelines extracted by this skill can be:
- Stored in `.claude/guidelines.json` for future retrieval
- Used by the kaizen system to improve agent behavior
- Displayed in conversation summaries
- Retrieved by the `guideline-retrieval` skill

## Saving Guidelines

After generating guidelines JSON, save them using the script:

```bash
echo '<guidelines_json>' | python3 scripts/save_guidelines.py
```

The script will:
- Find an existing guidelines file or create `.claude/guidelines.json`
- Append new guidelines (skipping duplicates)
- Print the actual storage path and count

**Environment variables:**
- `GUIDELINES_FILE`: Override the default storage location

## Best Practices

1. **Be specific**: Generic guidelines are less useful than context-specific ones
2. **Be actionable**: Guidelines should clearly state what to do
3. **Include rationale**: Explain why the approach works
4. **Use situational triggers**: Context-based triggers are more useful than failure-based ones
5. **Limit to 3-5 guidelines**: Focus on the most impactful learnings
