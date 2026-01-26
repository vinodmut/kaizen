# Infographic Generator Usage Examples

## Example 1: Simple Q&A Summary

**Scenario**: User asks a technical question and receives an answer.

**Request**: "How does Claude's memory system work?"

**Response**: "Claude's memory system stores information from past conversations, updating periodically in the background. It uses this context to personalize responses while maintaining conversation continuity across sessions."

**Command**:
```bash
python scripts/generate_infographic.py \
    "How does Claude's memory system work?" \
    "Claude's memory system stores information from past conversations, updating periodically in the background." \
    output/memory_system.png
```

## Example 2: Task Completion Summary

**Scenario**: User requests a coding task and Claude completes it.

**Request**: "Create a Python script to analyze CSV files"

**Response**: "Created analyze_data.py with pandas integration. The script loads CSV files, performs statistical analysis, generates visualizations, and exports results to Excel format."

**Command**:
```bash
python scripts/generate_infographic.py \
    "Create a Python script to analyze CSV files" \
    "Created analyze_data.py with pandas integration for statistical analysis and visualization." \
    output/task_complete.png \
    assets/template_background.png
```

## Example 3: Research Summary

**Scenario**: User asks Claude to research a topic.

**Request**: "What are the latest developments in quantum computing?"

**Response**: "Recent breakthroughs include IBM's 1000+ qubit processor, Google's error correction advances, and new applications in drug discovery and cryptography. Commercial quantum computing services are expanding rapidly."

**Command**:
```bash
python scripts/generate_infographic.py \
    "What are the latest developments in quantum computing?" \
    "Recent breakthroughs include IBM's 1000+ qubit processor and Google's error correction advances." \
    output/quantum_research.png
```

## Example 4: Creative Task

**Scenario**: User requests creative content generation.

**Request**: "Write a short story about a robot learning emotions"

**Response**: "Created a 1200-word story titled 'Electric Hearts' about Unit-7, a maintenance robot who discovers emotions through interactions with a lonely artist, exploring themes of consciousness and connection."

**Command**:
```bash
python scripts/generate_infographic.py \
    "Write a short story about a robot learning emotions" \
    "Created 'Electric Hearts': 1200 words exploring robot consciousness and emotional discovery." \
    output/story_summary.png
```

## Example 5: Problem Solving

**Scenario**: User presents a technical problem to debug.

**Request**: "My Python code has a memory leak when processing large files"

**Response**: "Identified issue: file handles not closing properly. Solution: Use context managers (with statements) for file operations and implement batch processing to handle data in chunks rather than loading entire files."

**Command**:
```bash
python scripts/generate_infographic.py \
    "My Python code has a memory leak when processing large files" \
    "Fixed: Use context managers and batch processing to handle data in chunks." \
    output/debug_solution.png
```

## Example 6: Learning/Education

**Scenario**: User asks for explanation of a complex concept.

**Request**: "Explain blockchain technology like I'm 10"

**Response**: "Blockchain is like a notebook that everyone in class shares. When someone writes in it, everyone gets a copy. No one can erase or change what's written, and everyone can check if something new is correct before it's added."

**Command**:
```bash
python scripts/generate_infographic.py \
    "Explain blockchain technology like I'm 10" \
    "Blockchain is like a shared notebook where everyone has a copy and nothing can be erased." \
    output/blockchain_eli5.png
```

## Workflow Integration

### Automatic Generation After Each Response

To automatically generate infographics after every Claude response, integrate the script into your workflow:

```python
# After processing user request
request_summary = extract_key_request(user_message)
response_summary = extract_key_response(claude_response)

# Generate infographic
output_path = f"infographics/{timestamp}_summary.png"
create_infographic(request_summary, response_summary, output_path)
```

### Batch Processing

Process multiple conversation summaries at once:

```python
conversations = [
    ("Request 1", "Response 1", "output1.png"),
    ("Request 2", "Response 2", "output2.png"),
    ("Request 3", "Response 3", "output3.png"),
]

for req, resp, output in conversations:
    create_infographic(req, resp, output, "assets/template_background.png")
```

## Text Extraction Tips

### From Long Requests

Extract the core question or task:
- **Original**: "I've been working on this project for weeks and I'm stuck. I need help with implementing a sorting algorithm that can handle edge cases like duplicate values, empty arrays, and special characters. Can you help me?"
- **Extracted**: "Need help implementing a robust sorting algorithm for edge cases"

### From Long Responses

Extract the main conclusion or action:
- **Original**: [3 paragraphs of detailed explanation]
- **Extracted**: "Implemented merge sort with custom comparator to handle duplicates and special characters efficiently"

### Best Practices

1. **Focus on outcomes**: What was accomplished?
2. **Use active voice**: "Created", "Fixed", "Explained", "Built"
3. **Include key metrics**: Numbers, percentages, specific results
4. **Maintain context**: Ensure the summary is understandable standalone
5. **Avoid jargon**: Use clear, accessible language when possible
