---
name: infographic-generator
description: Automatically generates visual infographic summaries of conversations between users and Claude. Use this skill AFTER processing any user request - it triggers on every utterance, after tool calls, and after responses are returned to create a visual summary of the request-response interaction. Creates PNG infographics with customizable layouts, colors, and templates.
---

# Infographic Generator

## Overview

This skill automatically generates visual infographic summaries of conversations, creating shareable PNG images that capture the essence of each request-response interaction. The infographics present both the user's question/request and Claude's response in a professional, visually appealing format suitable for sharing, documentation, or presentation purposes.

## Automatic Triggering

This skill should be invoked automatically at specific points in every conversation:

1. **After user utterance**: When the user submits a message
2. **After tool calls**: When Claude uses tools to process the request
3. **After response generation**: When Claude returns a response to the user

The skill creates a visual summary capturing the key elements of the interaction.

## Workflow

### Step 1: Extract Key Information

From the conversation, extract:

- **Request summary**: The core question, task, or request from the user (max 200 characters)
- **Response summary**: The main answer, outcome, or conclusion from Claude (max 300 characters)

**Text Extraction Guidelines**:

- Focus on the essential question or task, not preamble
- For responses, emphasize outcomes and actions taken
- Use active voice: "Created", "Fixed", "Explained", "Built"
- Keep language clear and accessible

**Examples**:

```
User: "I've been struggling with my Python code that processes CSV files..."
Extracted Request: "Debug Python CSV processing code with memory issues"

Claude: [3 paragraphs explaining the solution]
Extracted Response: "Fixed memory leak by implementing batch processing with context managers"
```

### Step 2: Install Dependencies

The script automatically handles dependency installation. If Pillow is not available, it will be installed with `--break-system-packages` flag:

```python
pip install --break-system-packages Pillow
```

### Step 3: Generate Infographic

Execute the generation script with the extracted information:

```bash
python scripts/generate_infographic.py \
    "<request_summary>" \
    "<response_summary>" \
    "output/infographic_<timestamp>.png" \
    "assets/template_background.png"
```

**Parameters**:
- `request_summary`: User's question or task (string)
- `response_summary`: Claude's response or outcome (string)
- `output_path`: Where to save the PNG file
- `template_path`: Optional background template (use provided template or omit for plain background)

**Outputs**:
- `<output_path>`: The infographic PNG image

### Step 4: Save and Present

Save the generated infographic to `/mnt/user-data/outputs/` and present it to the user using the `present_files` tool.

## Quick Start Example

```bash
# Generate an infographic for a typical interaction
python scripts/generate_infographic.py \
    "How does machine learning work?" \
    "Machine learning enables systems to learn from data and improve performance without explicit programming through pattern recognition and statistical methods." \
    output/ml_summary.png \
    assets/template_background.png
```

## Customization

### Using Custom Templates

The skill includes a default gradient template in `assets/template_background.png`. To use custom branding:

1. Place your custom background image (1200x800px) in the `assets/` directory
2. Reference it in the script call as the fourth parameter

### Adjusting Colors and Layout

For detailed customization of colors, fonts, layout, and dimensions, see `references/customization_guide.md`.

## Resources

### scripts/

**generate_infographic.py**: Main Python script for creating infographic images
- Handles text wrapping and layout
- Auto-installs Pillow dependency if needed
- Supports custom templates and styling
- Outputs high-quality PNG files (95% quality)

### references/

**customization_guide.md**: Complete reference for visual customization
- Color schemes and palettes
- Layout specifications and dimensions
- Font configuration
- Template requirements
- API usage documentation

**usage_examples.md**: Real-world examples and integration patterns
- Example conversations and their infographics
- Text extraction best practices
- Workflow integration code
- Batch processing examples

### assets/

**template_background.png**: Default gradient background template (1200x800px)
- Subtle blue-to-white gradient
- Semi-transparent accent elements
- Professional, clean design
- Ready to use or customize

## Output Specifications

### Infographic Image
- **Format**: PNG
- **Dimensions**: 1200x800px (3:2 aspect ratio)
- **Quality**: 95% (high quality, optimized file size)
- **Typical file size**: 200-500KB
- **Color space**: RGB

## Integration Pattern

For seamless integration into Claude's workflow:

```python
from datetime import datetime

# After processing user request
request_key = extract_core_request(user_message)  # Max 200 chars
response_key = extract_main_outcome(claude_response)  # Max 300 chars

# Generate visual summary
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"/mnt/user-data/outputs/infographic_{timestamp}.png"

import subprocess
cmd = [
    "python3",
    "scripts/generate_infographic.py",
    request_key,
    response_key,
    output_path,
    "assets/template_background.png"
]

subprocess.run(cmd)

# Present to user
present_files([output_path])
```

## Best Practices

1. **Automatic execution**: Invoke this skill after every response to maintain visual documentation
2. **Concise summaries**: Keep text brief and focused on core elements
3. **Consistent branding**: Use the provided template for visual consistency
4. **Meaningful outputs**: Ensure summaries are understandable without additional context
5. **File management**: Use timestamps in filenames to prevent overwrites
