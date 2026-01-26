---
name: trajectory-tips
description: Extract actionable guidelines from conversation trajectories. Analyzes user requests, steps taken, successes and failures to generate proactive tips that help on similar future tasks.
---

# Trajectory Tips Extractor

## Overview

This skill analyzes conversation trajectories to extract actionable guidelines that would help on similar tasks in the future. It transforms reactive learnings (what failed) into proactive recommendations (what to do first).

## Workflow

### Step 1: Analyze the Conversation

Identify from your current conversation:

- **Task/Request**: What was the user asking for?
- **Steps Taken**: What reasoning, actions, and observations occurred?
- **What Worked**: Which approaches succeeded?
- **What Failed**: Which approaches didn't work and why?

### Step 2: Extract Tips

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

### Step 3: Output Tips JSON

Output tips in the following JSON format:

```json
{
  "tips": [
    {
      "content": "Proactive guideline stating what TO DO",
      "rationale": "Why this approach works better",
      "category": "strategy|recovery|optimization",
      "trigger": "Situational context when this applies"
    }
  ]
}
```

## Tip Categories

- **strategy**: High-level approach or methodology choices
- **recovery**: Handling errors, edge cases, or unexpected situations
- **optimization**: Improving efficiency, performance, or code quality

## Examples

### Good vs Bad Tips

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

### references/

**tip_schema.md**: Complete JSON schema reference for tip structure

**good_bad_examples.md**: Extended collection of good vs bad tip examples across different scenarios

## Integration

Tips extracted by this skill can be:
- Stored in a knowledge base for future retrieval
- Used by the kaizen system to improve agent behavior
- Displayed in conversation summaries
- Fed into guidelines systems

## Best Practices

1. **Be specific**: Generic tips are less useful than context-specific ones
2. **Be actionable**: Tips should clearly state what to do
3. **Include rationale**: Explain why the approach works
4. **Use situational triggers**: Context-based triggers are more useful than failure-based ones
5. **Limit to 3-5 tips**: Focus on the most impactful learnings
