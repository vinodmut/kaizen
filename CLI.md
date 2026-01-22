# Kaizen CLI

Kaizen includes a command-line interface for managing namespaces and entities directly.

## Installation

The CLI is installed automatically with the package:

```bash
uv sync
```

## Commands

### Namespace Management

```bash
# List all namespaces
kaizen namespaces list

# Create a new namespace
kaizen namespaces create my_namespace

# Show namespace details
kaizen namespaces info my_namespace

# Delete a namespace (prompts for confirmation)
kaizen namespaces delete my_namespace

# Delete without confirmation
kaizen namespaces delete my_namespace --force
```

### Entity Management

```bash
# List all entities in a namespace
kaizen entities list my_namespace

# List entities filtered by type
kaizen entities list my_namespace --type guideline

# Add an entity
kaizen entities add my_namespace --content "Always write tests first" --type guideline

# Add entity without LLM-based conflict resolution (faster, no OpenAI key needed)
kaizen entities add my_namespace --content "Use descriptive names" --type guideline --no-conflict-resolution

# Add entity with metadata (JSON format)
kaizen entities add my_namespace --content "Check return values" --type guideline --metadata '{"source": "code-review"}'

# Search entities using semantic similarity
kaizen entities search my_namespace "testing best practices"

# Search with type filter
kaizen entities search my_namespace "error handling" --type guideline

# Show full details of an entity
kaizen entities show my_namespace 12345

# Delete an entity
kaizen entities delete my_namespace 12345
```

## Examples

```bash
# Create a namespace for coding guidelines
uv run kaizen namespaces create coding_guidelines

# Add some guidelines
uv run kaizen entities add coding_guidelines \
  --content "Always handle errors explicitly" \
  --type guideline \
  --no-conflict-resolution

uv run kaizen entities add coding_guidelines \
  --content "Write unit tests for all public functions" \
  --type guideline \
  --no-conflict-resolution

# Search for relevant guidelines
uv run kaizen entities search coding_guidelines "error handling"

# List all guidelines
uv run kaizen entities list coding_guidelines --type guideline
```

### Sync Commands

Sync commands import trajectories from external sources.

#### Claude Cowork Sync

Sync trajectories from Claude Cowork local agent mode sessions:

```bash
# Sync with default settings
kaizen sync claudecowork

# Sync with custom sessions directory
kaizen sync claudecowork --sessions-dir ~/custom/path

# Sync to a specific namespace
kaizen sync claudecowork --namespace my_namespace

# Limit number of sessions to process
kaizen sync claudecowork --limit 10
```

**Options:**
- `--sessions-dir, -d`: Claude Cowork sessions directory (default: platform-specific)
  - macOS: `~/Library/Application Support/Claude/local-agent-mode-sessions`
  - Windows: `%APPDATA%/Claude/local-agent-mode-sessions`
  - Linux: `~/.config/claude/local-agent-mode-sessions`
- `--namespace, -n`: Target namespace for storing trajectories
- `--limit`: Maximum number of sessions to process (default: 100)
- `--include-errors`: Include sessions with errors

**Environment Variables:**
- `CLAUDECOWORK_SESSIONS_DIR`: Override the default sessions directory

#### Phoenix Sync

Sync trajectories from Arize Phoenix observability platform:

```bash
# Sync from Phoenix
kaizen sync phoenix

# Sync with custom Phoenix URL
kaizen sync phoenix --url http://localhost:6006

# Sync from a specific project
kaizen sync phoenix --project my_project

# Sync to a specific namespace
kaizen sync phoenix --namespace my_namespace
```

**Options:**
- `--url, -u`: Phoenix server URL (default: `http://localhost:6006`)
- `--project, -p`: Phoenix project name (default: `default`)
- `--namespace, -n`: Target namespace for storing trajectories
- `--limit`: Maximum number of spans to fetch (default: 100)
- `--include-errors`: Include failed/error spans

**Environment Variables:**
- `PHOENIX_URL`: Override the default Phoenix URL
- `PHOENIX_PROJECT`: Override the default project name

## Environment Variables

The CLI uses the same environment variables as the MCP server. See the [Configuration](README.md#configuration) section in the main README.
