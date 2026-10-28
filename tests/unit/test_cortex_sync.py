"""Cortex session events -> OpenAI trajectories, with a per-session cursor."""

import json
from datetime import UTC, datetime

import httpx
import pytest

from altk_evolve.config.evolve import EvolveConfig
from altk_evolve.config.filesystem import FilesystemSettings
from altk_evolve.frontend.client.evolve_client import EvolveClient
from altk_evolve.schema.conflict_resolution import EntityUpdate
from altk_evolve.schema.guidelines import Guideline, GuidelineGenerationResult
from altk_evolve.sync.cortex_sync import (
    CortexCursorStore,
    CortexSessionClient,
    clean_text,
    ingest_session,
    is_main_turn,
    sync_cortex,
    turns_to_messages,
)

pytestmark = pytest.mark.unit
SID = "11111111-2222-3333-4444-555555555555"
SYSTEM = {"role": "system", "content": "You are Claude Code."}
TASK = {"role": "user", "content": "<system-reminder>\nproject rules\n</system-reminder>\n\nfix the failing test"}


def turn(seq, history, completion="", calls=(), results=(), **overrides):
    """A full main-agent response event as Cortex's session API serves it."""
    inference = {
        "agentRole": "main",
        "model": "claude-opus",
        "messages": history,
        "tools": [{"name": "Bash"}],
        "completion": completion,
        "toolCalls": [{"id": cid, "name": name, "arguments": json.dumps(args)} for cid, name, args in calls],
        "toolResults": [{"toolUseId": cid, "content": content, "isError": err} for cid, content, err in results],
    }
    event = {"seq": seq, "phase": "response", "direction": "outbound", "client": {"name": "claude-code"}, "inference": inference}
    event.update(overrides)
    return event


def summary(event):
    """The ``view=summary`` projection: bodies removed, counts kept."""
    inference = {k: v for k, v in event["inference"].items() if k not in ("messages", "tools", "toolCalls", "toolResults")}
    inference["messageCount"] = len(event["inference"]["messages"])
    inference["toolCount"] = len(event["inference"]["tools"])
    return {**event, "inference": inference}


def session_events():
    h1 = [SYSTEM, TASK]
    h2 = h1 + [{"role": "assistant", "content": "Running tests."}, {"role": "user", "content": ""}]
    h3 = h2 + [{"role": "assistant", "content": ""}, {"role": "user", "content": "use uv please"}]
    return [
        {"seq": 1, "phase": "request", "inference": {"messages": h1}},
        turn(2, h1, "Running tests.", calls=[("t1", "Bash", {"command": "pytest"})]),
        turn(3, [{"role": "user", "content": "title this"}], "Fix test", tools_override=True),
        turn(5, h2, "", calls=[("t2", "Bash", {"command": "cat x.py"})], results=[("t1", "1 failed", True)]),
        turn(7, h3, "Fixed with uv.", results=[("t2", "print(1)", False)]),
        {"seq": 8, "phase": "response", "tunnel": True},
    ]


def _fix_side_call(events):
    for event in events:
        if event.get("tools_override"):
            event.pop("tools_override")
            event["inference"]["tools"] = []
    return events


class FakeCortex:
    def __init__(self, events):
        self.events = {e["seq"]: e for e in _fix_side_call(events)}
        self.updated = "2026-10-28T10:00:00-05:00"

    def handler(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/v1/sessions":
            return httpx.Response(
                200, json={"sessions": [{"id": SID, "agent": "claude-code", "updatedAt": self.updated}, {"id": "default"}]}
            )
        if path == f"/v1/sessions/{SID}":
            assert request.url.params["view"] == "summary"
            return httpx.Response(
                200,
                json={
                    "id": SID,
                    "events": [summary(e) if e.get("inference", {}).get("tools") is not None else e for e in self.events.values()],
                },
            )
        if path.startswith(f"/v1/sessions/{SID}/events/"):
            return httpx.Response(200, json=self.events[int(path.rsplit("/", 1)[1])])
        return httpx.Response(404)

    def client(self):
        return CortexSessionClient("http://cortex.test", transport=httpx.MockTransport(self.handler))


def test_clean_text_strips_injected_blocks():
    text = 'hi <evolve-guidelines source="altk-evolve" ids="a">1. x</evolve-guidelines> <system-reminder>r</system-reminder> there'
    assert clean_text(text) == "hi   there"


def test_main_turn_filter():
    events = _fix_side_call(session_events())
    assert [e["seq"] for e in events if is_main_turn(e)] == [2, 5, 7]
    assert not is_main_turn(turn(9, [TASK], "x", subagent="agent-1"))
    assert not is_main_turn(turn(9, [TASK], "x", client={}))


def test_turns_to_messages_rebuilds_tool_calls_and_results():
    events = _fix_side_call(session_events())
    messages = turns_to_messages([e for e in events if is_main_turn(e)])
    assert [m["role"] for m in messages] == ["user", "assistant", "tool", "assistant", "tool", "user", "assistant"]
    assert messages[0] == {"role": "user", "content": "fix the failing test"}
    assert messages[1]["tool_calls"][0]["function"] == {"name": "Bash", "arguments": '{"command": "pytest"}'}
    assert messages[2] == {"role": "tool", "tool_call_id": "t1", "content": "[error] 1 failed"}
    assert messages[4] == {"role": "tool", "tool_call_id": "t2", "content": "print(1)"}
    assert messages[5] == {"role": "user", "content": "use uv please"}
    assert messages[6] == {"role": "assistant", "content": "Fixed with uv."}


def test_turns_to_messages_resets_after_compaction():
    first = turn(2, [SYSTEM, TASK, {"role": "assistant", "content": "a"}, {"role": "user", "content": "more"}], "ok")
    compacted = turn(4, [SYSTEM, {"role": "user", "content": "summary of earlier work"}], "continuing")
    messages = turns_to_messages([first, compacted])
    assert {"role": "user", "content": "summary of earlier work"} in messages


@pytest.fixture
def evolve(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("EVOLVE_HOOKS_CONFIG", "")
    from altk_evolve.config.guidelines import guidelines_settings

    monkeypatch.setattr(guidelines_settings, "guidelines_mode", "standard")
    seen = []

    def generate(messages, *, context_messages=None, options, outcome=None):
        seen.append((messages, context_messages))
        return [
            GuidelineGenerationResult(
                task_description="fix test",
                guidelines=[
                    Guideline(content=f"Use uv {len(seen)}", rationale="r", category="strategy", trigger="t", implementation_steps=[])
                ],
            )
        ]

    def resolve(candidates, incoming, settings=None):
        return [EntityUpdate(id=e.id, type=e.type, content=e.content, event="ADD") for e in incoming]

    monkeypatch.setattr("altk_evolve.llm.guidelines.guidelines.generate_guidelines", generate)
    monkeypatch.setattr("altk_evolve.llm.conflict_resolution.conflict_resolution.resolve_conflicts", resolve)
    client = EvolveClient(EvolveConfig(settings=FilesystemSettings(data_dir=str(tmp_path / "entities"))))
    return client, seen


def test_dry_run_converts_without_processing_or_moving_cursor(tmp_path):
    cursors = CortexCursorStore(tmp_path / "cursors.json")
    result = ingest_session(None, FakeCortex(session_events()).client(), SID, namespace_id="cortex", cursors=cursors, dry_run=True)
    assert result.status == "dry-run" and (result.first_seq, result.last_seq) == (2, 7)
    trajectory = result.trajectory
    assert trajectory["batch"] == {**trajectory["batch"], "source": "cortex", "conversation_id": SID, "batch_id": "2-7", "scope": "cortex"}
    assert trajectory["metadata"] == {"status": "candidate", "creation_mode": "auto-cortex", "agent_id": "claude-code", "session_id": SID}
    assert cursors.get(SID) == 0


def test_ingest_writes_candidates_and_advances_cursor(tmp_path, evolve):
    client, seen = evolve
    cortex = FakeCortex(session_events())
    cursors = CortexCursorStore(tmp_path / "cursors.json")

    result = ingest_session(client, cortex.client(), SID, namespace_id="cortex", cursors=cursors)

    assert result.status == "processed" and len(result.guidelines) == 1
    [guideline] = client.get_all_entities("cortex", filters={"type": "guideline"})
    assert guideline.metadata["status"] == "candidate"
    assert guideline.metadata["creation_mode"] == "auto-cortex"
    assert guideline.metadata["session_id"] == SID
    assert guideline.metadata["source_task_id"] == f"cortex:{SID}:7"
    assert cursors.get(SID) == 7
    assert client.select_guidelines("cortex", "fix test", statuses={"active"}).all == []

    again = ingest_session(client, cortex.client(), SID, namespace_id="cortex", cursors=cursors)
    assert again.status == "up-to-date" and len(seen) == 1


def test_later_turns_learn_only_new_material_with_task_context(tmp_path, evolve):
    client, seen = evolve
    events = session_events()
    cortex = FakeCortex(events[:3])  # first turn only (plus the side call)
    cursors = CortexCursorStore(tmp_path / "cursors.json")

    assert ingest_session(client, cortex.client(), SID, namespace_id="cortex", cursors=cursors, min_new_turns=1).status == "processed"
    cortex.events.update({e["seq"]: e for e in events[3:]})
    result = ingest_session(client, cortex.client(), SID, namespace_id="cortex", cursors=cursors)

    assert (result.first_seq, result.last_seq) == (5, 7)
    messages, context = seen[-1]
    assert context == [{"role": "user", "content": "fix the failing test"}]
    assert messages[0] == {"role": "tool", "tool_call_id": "t1", "content": "[error] 1 failed"}
    assert all(m.get("content") != "fix the failing test" for m in messages)


def test_too_few_new_turns_keeps_cursor(tmp_path):
    cursors = CortexCursorStore(tmp_path / "cursors.json")
    cortex = FakeCortex(session_events()[:3])
    result = ingest_session(None, cortex.client(), SID, namespace_id="cortex", cursors=cursors)
    assert result.status == "too-few-turns" and cursors.get(SID) == 0


def test_sync_selects_idle_sessions(tmp_path):
    cursors = CortexCursorStore(tmp_path / "cursors.json")
    cortex = FakeCortex(session_events())
    busy = sync_cortex(
        None,
        cortex.client(),
        namespace_id="cortex",
        cursors=cursors,
        idle_minutes=15,
        dry_run=True,
        now=datetime(2026, 10, 28, 15, 5, tzinfo=UTC),
    )
    assert busy == []
    idle = sync_cortex(
        None,
        cortex.client(),
        namespace_id="cortex",
        cursors=cursors,
        idle_minutes=15,
        dry_run=True,
        now=datetime(2026, 10, 28, 16, 0, tzinfo=UTC),
    )
    assert [(r.session_id, r.status) for r in idle] == [(SID, "dry-run")]


def test_sync_reports_errors_per_session(tmp_path):
    cursors = CortexCursorStore(tmp_path / "cursors.json")
    broken = CortexSessionClient("http://cortex.test", transport=httpx.MockTransport(lambda r: httpx.Response(500)))
    [result] = sync_cortex(None, broken, namespace_id="cortex", cursors=cursors, session_ids=[SID])
    assert result.status.startswith("error")
