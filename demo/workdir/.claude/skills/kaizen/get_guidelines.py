#!/usr/bin/env python3
"""Call Kaizen MCP server to get guidelines for a task."""

import json
import sys
import httpx

#MCP_URL = "http://localhost:8201/mcp"
MCP_URL = "https://66f7a587a584.ngrok-free.app/mcp"


def parse_sse_response(text: str) -> dict:
    """Parse SSE response to extract JSON data."""
    for line in text.strip().split("\n"):
        if line.startswith("data: "):
            return json.loads(line[6:])
    return {}


def get_guidelines(task: str) -> str:
    """Call the Kaizen MCP server to get guidelines."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    with httpx.Client() as client:
        # Initialize session
        init_resp = client.post(
            MCP_URL,
            json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "kaizen-skill", "version": "1.0"}
                }
            },
            headers=headers
        )
        session_id = init_resp.headers.get("mcp-session-id")

        # Call get_guidelines tool
        tool_headers = {**headers, "mcp-session-id": session_id}
        tool_resp = client.post(
            MCP_URL,
            json={
                "jsonrpc": "2.0",
                "id": "2",
                "method": "tools/call",
                "params": {
                    "name": "get_guidelines",
                    "arguments": {"task": task}
                }
            },
            headers=tool_headers
        )

        result = parse_sse_response(tool_resp.text)
        if "result" in result:
            return result["result"]["content"][0]["text"]
        elif "error" in result:
            return f"Error: {result['error']['message']}"
        return "No response"


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "general coding task"
    print(get_guidelines(task))
