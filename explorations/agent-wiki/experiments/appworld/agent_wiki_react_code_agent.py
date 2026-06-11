"""AppWorld ReAct wrapper that lets the agent follow an agent-wiki.

This module is intended to be imported before AppWorld constructs the agent.
Importing it registers `agent_wiki_react_code_agent` in AppWorld's simplified
agent registry.

The wrapper deliberately does not implement retrieval. It appends a compact
instruction to the existing ReAct task message and asks the model to read the
wiki's AGENTS.md and follow the wiki's own retrieval procedure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from appworld import AppWorld
from appworld_agents.code.simplified.agent import Agent
from appworld_agents.code.simplified.react_code_agent import SimplifiedReActCodeAgent


WikiAccessMode = Literal["direct_file", "prompt_index"]


@Agent.register("agent_wiki_react_code_agent")
class AgentWikiReActCodeAgent(SimplifiedReActCodeAgent):  # type: ignore[misc]
    """Thin ReAct subclass that injects an agent-wiki consult instruction.

    Parameters are intentionally simple so they can be set in AppWorld's agent
    config JSON/Jsonnet.
    """

    def __init__(
        self,
        wiki_root: str | None = None,
        wiki_arm: str = "wiki",
        wiki_access_mode: WikiAccessMode = "direct_file",
        prompt_index_char_budget: int = 12000,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.wiki_root = wiki_root
        self.wiki_arm = wiki_arm
        self.wiki_access_mode: WikiAccessMode = wiki_access_mode
        self.prompt_index_char_budget = prompt_index_char_budget

    def initialize(self, world: AppWorld) -> None:
        super().initialize(world)
        if not self.wiki_root:
            return
        block = self._wiki_instruction_block(world)
        self._append_to_current_task_message(block)
        self.logger.show_message(
            role="user",
            content=json.dumps(
                {
                    "agent_wiki_event": "wiki_instruction_injected",
                    "wiki_arm": self.wiki_arm,
                    "wiki_root": str(Path(self.wiki_root).expanduser()),
                    "wiki_access_mode": self.wiki_access_mode,
                },
                indent=2,
            ),
            step_number=0,
        )

    def _wiki_instruction_block(self, world: AppWorld) -> str:
        wiki_root = Path(self.wiki_root or "").expanduser().resolve()
        agents_md = wiki_root / "AGENTS.md"
        index_jsonl = wiki_root / "_index.jsonl"

        header = [
            "",
            "Additional memory instruction:",
            "",
            f"- This run has an agent-wiki memory root for the `{self.wiki_arm}` arm: `{wiki_root}`.",
            "- Before solving the task, consult the wiki's `AGENTS.md` and follow its retrieval procedure.",
            "- Use only relevant memories. Do not read every wiki page.",
            "- Treat wiki content as prior experience, not ground truth. The current AppWorld task and API outputs are authoritative.",
            "- Continue to follow all AppWorld task-completion rules, including calling `apis.supervisor.complete_task`.",
        ]

        if self.wiki_access_mode == "direct_file":
            header.extend(
                [
                    "",
                    "Suggested first code step if local file reads are available:",
                    "",
                    "```python",
                    "from pathlib import Path",
                    f"wiki_root = Path({str(wiki_root)!r})",
                    "print((wiki_root / 'AGENTS.md').read_text()[:4000])",
                    "```",
                    "",
                    "Then follow `AGENTS.md`. Read only the files it says are needed for this exact task.",
                ]
            )
            return "\n".join(header)

        if self.wiki_access_mode != "prompt_index":
            raise ValueError(f"Unsupported wiki_access_mode: {self.wiki_access_mode}")

        agents_text = _read_text_or_note(agents_md, "AGENTS.md")
        index_text = _read_text_or_note(index_jsonl, "_index.jsonl")
        combined = (
            "\n".join(header)
            + "\n\n"
            + "The local REPL may not be able to read files directly, so the wiki contract and retrieval index are provided below.\n\n"
            + "----- AGENTS.md -----\n"
            + agents_text
            + "\n\n----- _index.jsonl -----\n"
            + index_text
        )
        return _truncate_middle(combined, self.prompt_index_char_budget)

    def _append_to_current_task_message(self, block: str) -> None:
        if not self.messages:
            raise ValueError("ReAct messages are not initialized.")
        last = self.messages[-1]
        if last.get("role") != "user":
            self.messages.append({"role": "user", "content": block})
            return
        content = last.get("content")
        if not isinstance(content, str):
            raise ValueError("Expected final ReAct task message content to be a string.")
        last["content"] = content.rstrip() + "\n\n" + block.strip() + "\n"


def _read_text_or_note(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"[Could not read {label} at {path}: {exc}]"


def _truncate_middle(text: str, char_budget: int) -> str:
    if char_budget <= 0 or len(text) <= char_budget:
        return text
    head_budget = max(0, char_budget // 2)
    tail_budget = max(0, char_budget - head_budget)
    return text[:head_budget] + "\n\n[...TRUNCATED...]\n\n" + text[-tail_budget:]
