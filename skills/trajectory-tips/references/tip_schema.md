# Tip JSON Schema Reference

## Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["tips"],
  "properties": {
    "tips": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["content", "category", "trigger"],
        "properties": {
          "content": {
            "type": "string",
            "description": "The actionable guideline or recommendation",
            "maxLength": 200
          },
          "rationale": {
            "type": "string",
            "description": "Explanation of why this approach works",
            "maxLength": 300
          },
          "category": {
            "type": "string",
            "enum": ["strategy", "recovery", "optimization"],
            "description": "Classification of the tip type"
          },
          "trigger": {
            "type": "string",
            "description": "Situational context when this tip applies",
            "maxLength": 150
          }
        }
      },
      "minItems": 1,
      "maxItems": 5
    }
  }
}
```

## Field Descriptions

### content (required)
The main actionable guideline. Should be:
- Written in imperative or declarative form
- Specific and actionable
- Proactive (stating what TO DO, not what to avoid)

### rationale (optional but recommended)
Explains why this approach works better than alternatives. Helps users understand the reasoning and apply the tip appropriately.

### category (required)
One of three values:

| Category | Description | Example |
|----------|-------------|---------|
| `strategy` | High-level approach or methodology | "Use Python libraries for portability" |
| `recovery` | Error handling and edge cases | "Validate file existence before processing" |
| `optimization` | Performance and efficiency | "Use batch processing for large datasets" |

### trigger (required)
Describes the situational context when this tip applies. Should be:
- Based on context, not failure conditions
- Specific enough to be useful
- General enough to apply broadly

## Example Output

```json
{
  "tips": [
    {
      "content": "Use Python PIL/Pillow for image metadata extraction in sandboxed environments",
      "rationale": "System tools like exiftool may not be available; PIL is always installable via pip",
      "category": "strategy",
      "trigger": "When extracting image metadata in containerized or sandboxed environments"
    },
    {
      "content": "Check for existing lock files before choosing a package manager",
      "rationale": "Projects may already have yarn.lock or package-lock.json indicating preferred tooling",
      "category": "strategy",
      "trigger": "When installing dependencies in an unfamiliar project"
    },
    {
      "content": "Implement batch processing with context managers for large file operations",
      "rationale": "Prevents memory leaks and ensures proper resource cleanup",
      "category": "optimization",
      "trigger": "When processing files larger than available memory"
    }
  ]
}
```
