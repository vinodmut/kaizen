# Claude Code Demo

This guide walks through running Kaizen with Claude Code.

## Prerequisites

- Kaizen MCP server running (see [README.md](README.md))
- [Claude Code](https://code.claude.com/docs/en/overview) installed with credentials configured

## Running the Filesystem MCP Server

The demo uses a filesystem MCP server to give Claude Code access to files:

```bash
uv run demo/filesystem/server.py demo/filesystem --transport sse --port 8202
```

## Running with Claude Code

```bash
(cd demo/workdir && claude)
```

Add the MCP servers if needed:
```bash
claude mcp add --scope local guidelines --transport sse http://localhost:8201/sse
claude mcp add --scope local filesystem --transport sse http://localhost:8202/sse
```

Test with:
```
What states do I have teammates in? Read the list from the states.txt file.
```

## Using the Kaizen Skill

A Claude Code skill is available at `demo/workdir/.claude/skills/kaizen/` that fetches guidelines directly from the Kaizen MCP server.

### Prerequisites

- `httpx` package installed (`pip install httpx`)
- Kaizen MCP server running on port 8201:
  ```bash
  KAIZEN_RETURN_ALL_GUIDELINES=true KAIZEN_BACKEND=filesystem uv run fastmcp run kaizen/frontend/mcp/mcp_server.py --transport http --port 8201
  ```

### Usage

Invoke the skill in Claude Code:
```
/kaizen implement user authentication
```

Or test the script directly:
```bash
python3 demo/workdir/.claude/skills/kaizen/get_guidelines.py "implement error handling"
```
