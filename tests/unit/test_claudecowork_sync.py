"""Tests for Claude Cowork Sync functionality."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kaizen.sync.claudecowork_sync import ClaudeCoworkSync, ClaudeCoworkSession
from kaizen.sync.phoenix_sync import SyncResult

# Mark all tests in this module as claudecowork tests
pytestmark = pytest.mark.claudecowork


@pytest.fixture
def temp_sessions_dir():
    """Create a temporary sessions directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_session(temp_sessions_dir):
    """Create a sample session in the temp directory."""
    # Create nested structure: {sessions_dir}/{uuid1}/{uuid2}/local_{session_id}/
    uuid1 = "e8919ce0-7f88-478c-9c7c-3b318a9c0154"
    uuid2 = "1640016c-9db2-4985-a07b-51674bdee369"
    session_id = "test-session-123"

    session_dir = temp_sessions_dir / uuid1 / uuid2 / f"local_{session_id}"
    session_dir.mkdir(parents=True)

    # Create metadata file
    metadata = {
        "sessionId": f"local_{session_id}",
        "title": "Test Session",
        "model": "claude-sonnet-4",
        "createdAt": 1700000000000,
        "lastActivityAt": 1700001000000,
    }
    metadata_file = session_dir.parent / f"local_{session_id}.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f)

    # Create audit.jsonl with sample events
    audit_events = [
        {
            "type": "user",
            "message": {"role": "user", "content": "Hello, world!"},
            "_audit_timestamp": "2024-01-15T10:00:00Z",
        },
        {
            "type": "system",
            "subtype": "init",
            "session_id": session_id,
            "_audit_timestamp": "2024-01-15T10:00:01Z",
        },
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello! How can I help?"}],
            },
            "_audit_timestamp": "2024-01-15T10:00:02Z",
        },
        {
            "type": "result",
            "subtype": "success",
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "cache_read_input_tokens": 10,
            },
            "_audit_timestamp": "2024-01-15T10:00:03Z",
        },
    ]

    audit_file = session_dir / "audit.jsonl"
    with open(audit_file, "w") as f:
        for event in audit_events:
            f.write(json.dumps(event) + "\n")

    return {
        "session_id": session_id,
        "session_dir": session_dir,
        "metadata_file": metadata_file,
        "audit_file": audit_file,
        "metadata": metadata,
        "audit_events": audit_events,
    }


@pytest.fixture
def claudecowork_sync(temp_sessions_dir):
    """Create a ClaudeCoworkSync instance with mocked client."""
    with patch("kaizen.sync.claudecowork_sync.KaizenClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        sync = ClaudeCoworkSync(
            sessions_dir=str(temp_sessions_dir),
            namespace_id="test_namespace",
        )
        sync.client = mock_client
        yield sync


# =============================================================================
# Session Discovery Tests
# =============================================================================


@pytest.mark.unit
class TestDiscoverSessions:
    """Tests for _discover_sessions method."""

    def test_discover_sessions_finds_session(self, claudecowork_sync, sample_session):
        """Test that sessions are discovered correctly."""
        sessions = claudecowork_sync._discover_sessions(limit=100)

        assert len(sessions) == 1
        session = sessions[0]
        assert session.session_id == sample_session["session_id"]
        assert session.title == "Test Session"
        assert session.model == "claude-sonnet-4"

    def test_discover_sessions_empty_dir(self, claudecowork_sync):
        """Test discovery with empty sessions directory."""
        sessions = claudecowork_sync._discover_sessions(limit=100)
        assert sessions == []

    def test_discover_sessions_nonexistent_dir(self):
        """Test discovery with non-existent directory."""
        with patch("kaizen.sync.claudecowork_sync.KaizenClient"):
            sync = ClaudeCoworkSync(
                sessions_dir="/nonexistent/path",
                namespace_id="test_namespace",
            )
            sessions = sync._discover_sessions(limit=100)
            assert sessions == []

    def test_discover_sessions_respects_limit(self, temp_sessions_dir, claudecowork_sync):
        """Test that limit is respected."""
        # Create multiple sessions
        for i in range(5):
            uuid1 = f"uuid1-{i}"
            uuid2 = f"uuid2-{i}"
            session_id = f"session-{i}"

            session_dir = temp_sessions_dir / uuid1 / uuid2 / f"local_{session_id}"
            session_dir.mkdir(parents=True)

            metadata = {
                "sessionId": f"local_{session_id}",
                "title": f"Session {i}",
                "model": "claude-sonnet-4",
                "createdAt": 1700000000000 + i * 1000,
                "lastActivityAt": 1700001000000 + i * 1000,
            }
            metadata_file = session_dir.parent / f"local_{session_id}.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f)

            audit_file = session_dir / "audit.jsonl"
            with open(audit_file, "w") as f:
                f.write(json.dumps({"type": "user", "message": {"content": "test"}}) + "\n")

        sessions = claudecowork_sync._discover_sessions(limit=3)
        assert len(sessions) == 3


# =============================================================================
# Audit Event Conversion Tests
# =============================================================================


@pytest.mark.unit
class TestConvertAuditEventToOpenAI:
    """Tests for _convert_audit_event_to_openai method."""

    def test_convert_user_message_string(self, claudecowork_sync):
        """Test converting a simple user message with string content."""
        event = {
            "type": "user",
            "message": {"role": "user", "content": "Hello, world!"},
        }
        result = claudecowork_sync._convert_audit_event_to_openai(event)
        assert result == {"role": "user", "content": "Hello, world!"}

    def test_convert_user_message_tool_result(self, claudecowork_sync):
        """Test converting a user message with tool_result blocks."""
        event = {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool_123",
                        "content": "File contents here",
                        "is_error": False,
                    }
                ],
            },
        }
        result = claudecowork_sync._convert_audit_event_to_openai(event)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["role"] == "tool"
        assert result[0]["tool_call_id"] == "tool_123"
        assert result[0]["content"] == "File contents here"

    def test_convert_assistant_message_text(self, claudecowork_sync):
        """Test converting an assistant message with text."""
        event = {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello! How can I help?"}],
            },
        }
        result = claudecowork_sync._convert_audit_event_to_openai(event)
        assert result["role"] == "assistant"
        assert result["content"] == "Hello! How can I help?"

    def test_convert_assistant_message_string_content(self, claudecowork_sync):
        """Test converting an assistant message with string content."""
        event = {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": "Direct string response",
            },
        }
        result = claudecowork_sync._convert_audit_event_to_openai(event)
        assert result["role"] == "assistant"
        assert result["content"] == "Direct string response"

    def test_convert_assistant_message_tool_use(self, claudecowork_sync):
        """Test converting an assistant message with tool_use."""
        event = {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_123",
                        "name": "Bash",
                        "input": {"command": "ls -la"},
                    }
                ],
            },
        }
        result = claudecowork_sync._convert_audit_event_to_openai(event)
        assert result["role"] == "assistant"
        assert "tool_calls" in result
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["id"] == "toolu_123"
        assert result["tool_calls"][0]["function"]["name"] == "Bash"
        assert json.loads(result["tool_calls"][0]["function"]["arguments"]) == {
            "command": "ls -la"
        }

    def test_convert_assistant_message_thinking(self, claudecowork_sync):
        """Test converting an assistant message with thinking block."""
        event = {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "Let me analyze this..."},
                    {"type": "text", "text": "The answer is 42."},
                ],
            },
        }
        result = claudecowork_sync._convert_audit_event_to_openai(event)
        assert result["role"] == "assistant"
        assert result["thinking"] == "Let me analyze this..."
        assert result["content"] == "The answer is 42."

    def test_convert_system_event_skipped(self, claudecowork_sync):
        """Test that system events are skipped."""
        event = {
            "type": "system",
            "subtype": "init",
            "session_id": "test",
        }
        result = claudecowork_sync._convert_audit_event_to_openai(event)
        assert result is None

    def test_convert_result_event_skipped(self, claudecowork_sync):
        """Test that result events are skipped."""
        event = {
            "type": "result",
            "subtype": "success",
            "usage": {"input_tokens": 100},
        }
        result = claudecowork_sync._convert_audit_event_to_openai(event)
        assert result is None

    def test_convert_filters_no_content(self, claudecowork_sync):
        """Test that '(no content)' text is filtered out."""
        event = {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "(no content)"},
                    {"type": "text", "text": "Real content"},
                ],
            },
        }
        result = claudecowork_sync._convert_audit_event_to_openai(event)
        assert result["content"] == "Real content"


# =============================================================================
# Trajectory Extraction Tests
# =============================================================================


@pytest.mark.unit
class TestExtractTrajectory:
    """Tests for _extract_trajectory method."""

    def test_extract_trajectory_basic(self, claudecowork_sync, sample_session):
        """Test extracting a basic trajectory."""
        session = ClaudeCoworkSession(
            session_id=sample_session["session_id"],
            session_dir=sample_session["session_dir"],
            metadata_file=sample_session["metadata_file"],
            audit_file=sample_session["audit_file"],
            title="Test Session",
            model="claude-sonnet-4",
            created_at=1700000000000,
            last_activity_at=1700001000000,
        )

        trajectory = claudecowork_sync._extract_trajectory(
            sample_session["audit_events"], session
        )

        assert trajectory["session_id"] == sample_session["session_id"]
        assert trajectory["title"] == "Test Session"
        assert trajectory["model"] == "claude-sonnet-4"
        assert len(trajectory["messages"]) == 2  # user + assistant (system skipped)
        assert trajectory["usage"]["input_tokens"] == 100
        assert trajectory["usage"]["output_tokens"] == 50

    def test_extract_trajectory_with_tool_calls(self, claudecowork_sync):
        """Test extracting trajectory with tool calls and results."""
        audit_events = [
            {
                "type": "user",
                "message": {"role": "user", "content": "List files"},
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "I'll list the files."},
                        {
                            "type": "tool_use",
                            "id": "toolu_1",
                            "name": "Bash",
                            "input": {"command": "ls"},
                        },
                    ],
                },
            },
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "toolu_1",
                            "content": "file1.txt\nfile2.txt",
                        }
                    ],
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "Here are the files."},
                    ],
                },
            },
        ]

        session = ClaudeCoworkSession(
            session_id="test",
            session_dir=Path("/tmp"),
            metadata_file=Path("/tmp/test.json"),
            audit_file=Path("/tmp/audit.jsonl"),
        )

        trajectory = claudecowork_sync._extract_trajectory(audit_events, session)
        messages = trajectory["messages"]

        # Should have: user, assistant with tool_call, tool result, assistant
        assert len(messages) == 4
        assert messages[0]["role"] == "user"
        assert "tool_calls" in messages[1]
        assert messages[2]["role"] == "tool"
        assert messages[3]["role"] == "assistant"


# =============================================================================
# Trajectory Cleaning Tests
# =============================================================================


@pytest.mark.unit
class TestCleanTrajectory:
    """Tests for _clean_trajectory method."""

    def test_clean_removes_system_reminders(self, claudecowork_sync):
        """Test that system reminders are removed."""
        trajectory = {
            "session_id": "test",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello <system-reminder>This is a reminder</system-reminder> there",
                }
            ],
        }
        cleaned = claudecowork_sync._clean_trajectory(trajectory)
        assert "<system-reminder>" not in cleaned["messages"][0]["content"]
        assert "Hello" in cleaned["messages"][0]["content"]
        assert "there" in cleaned["messages"][0]["content"]

    def test_clean_removes_multiline_system_reminders(self, claudecowork_sync):
        """Test that multiline system reminders are removed."""
        trajectory = {
            "session_id": "test",
            "messages": [
                {
                    "role": "assistant",
                    "content": "Start\n<system-reminder>\nLine 1\nLine 2\n</system-reminder>\nEnd",
                }
            ],
        }
        cleaned = claudecowork_sync._clean_trajectory(trajectory)
        assert "<system-reminder>" not in cleaned["messages"][0]["content"]
        assert "Start" in cleaned["messages"][0]["content"]
        assert "End" in cleaned["messages"][0]["content"]

    def test_clean_removes_empty_messages(self, claudecowork_sync):
        """Test that empty messages are removed."""
        trajectory = {
            "session_id": "test",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": ""},
                {"role": "assistant", "content": None},
                {"role": "user", "content": "World"},
            ],
        }
        cleaned = claudecowork_sync._clean_trajectory(trajectory)
        assert len(cleaned["messages"]) == 2
        assert cleaned["messages"][0]["content"] == "Hello"
        assert cleaned["messages"][1]["content"] == "World"

    def test_clean_preserves_tool_calls(self, claudecowork_sync):
        """Test that messages with tool_calls but no content are preserved."""
        trajectory = {
            "session_id": "test",
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [{"id": "1", "function": {"name": "test"}}],
                }
            ],
        }
        cleaned = claudecowork_sync._clean_trajectory(trajectory)
        assert len(cleaned["messages"]) == 1
        assert "tool_calls" in cleaned["messages"][0]


# =============================================================================
# Sync Tests
# =============================================================================


@pytest.mark.unit
class TestSync:
    """Tests for sync method."""

    def test_sync_creates_namespace_if_not_exists(self, claudecowork_sync, sample_session):
        """Test that sync creates namespace if it doesn't exist."""
        from kaizen.schema.exceptions import NamespaceNotFoundException

        claudecowork_sync.client.get_namespace_details.side_effect = (
            NamespaceNotFoundException()
        )
        claudecowork_sync.client.search_entities.return_value = []

        with patch.object(claudecowork_sync, "_process_trajectory", return_value=0):
            claudecowork_sync.sync(limit=10)

        claudecowork_sync.client.create_namespace.assert_called_once_with(
            "test_namespace"
        )

    def test_sync_skips_already_processed(self, claudecowork_sync, sample_session):
        """Test that already processed sessions are skipped."""
        mock_entity = MagicMock()
        mock_entity.metadata = {"session_id": sample_session["session_id"]}
        claudecowork_sync.client.search_entities.return_value = [mock_entity]

        result = claudecowork_sync.sync(limit=10)

        assert result.skipped == 1
        assert result.processed == 0

    @patch("kaizen.sync.claudecowork_sync.generate_tips")
    def test_sync_processes_new_sessions(self, mock_generate_tips, claudecowork_sync, sample_session):
        """Test that new sessions are processed."""
        claudecowork_sync.client.search_entities.return_value = []
        mock_generate_tips.return_value = []

        result = claudecowork_sync.sync(limit=10)

        assert result.processed == 1
        assert result.skipped == 0
        claudecowork_sync.client.update_entities.assert_called()

    @patch("kaizen.sync.claudecowork_sync.generate_tips")
    def test_sync_generates_tips(self, mock_generate_tips, claudecowork_sync, sample_session):
        """Test that tips are generated from trajectories."""
        claudecowork_sync.client.search_entities.return_value = []

        mock_tip = MagicMock()
        mock_tip.content = "Tip content"
        mock_tip.category = "strategy"
        mock_tip.rationale = "Tip rationale"
        mock_tip.trigger = "Tip trigger"
        mock_generate_tips.return_value = [mock_tip]

        result = claudecowork_sync.sync(limit=10)

        assert result.processed == 1
        assert result.tips_generated == 1

    def test_sync_returns_sync_result(self, claudecowork_sync, sample_session):
        """Test that sync returns a SyncResult."""
        claudecowork_sync.client.search_entities.return_value = []

        with patch.object(claudecowork_sync, "_process_trajectory", return_value=2):
            result = claudecowork_sync.sync(limit=10)

        assert isinstance(result, SyncResult)
        assert result.processed >= 0
        assert result.skipped >= 0
        assert result.tips_generated >= 0
        assert isinstance(result.errors, list)


# =============================================================================
# Helper Method Tests
# =============================================================================


@pytest.mark.unit
class TestHelperMethods:
    """Tests for helper methods."""

    def test_extract_tool_result_content_string(self, claudecowork_sync):
        """Test extracting string content from tool result."""
        result = claudecowork_sync._extract_tool_result_content("simple string")
        assert result == "simple string"

    def test_extract_tool_result_content_list(self, claudecowork_sync):
        """Test extracting list content from tool result."""
        content = [
            {"type": "text", "text": "Line 1"},
            {"type": "text", "text": "Line 2"},
        ]
        result = claudecowork_sync._extract_tool_result_content(content)
        assert "Line 1" in result
        assert "Line 2" in result

    def test_extract_tool_result_content_other(self, claudecowork_sync):
        """Test extracting other types of content."""
        result = claudecowork_sync._extract_tool_result_content(12345)
        assert result == "12345"

    def test_get_processed_session_ids_empty(self, claudecowork_sync):
        """Test getting processed IDs when none exist."""
        claudecowork_sync.client.search_entities.return_value = []

        result = claudecowork_sync._get_processed_session_ids()

        assert result == set()

    def test_get_processed_session_ids_with_entities(self, claudecowork_sync):
        """Test getting processed IDs from existing entities."""
        entity1 = MagicMock()
        entity1.metadata = {"session_id": "session_1"}
        entity2 = MagicMock()
        entity2.metadata = {"session_id": "session_2"}
        entity3 = MagicMock()
        entity3.metadata = None

        claudecowork_sync.client.search_entities.return_value = [
            entity1,
            entity2,
            entity3,
        ]

        result = claudecowork_sync._get_processed_session_ids()

        assert result == {"session_1", "session_2"}

    def test_get_processed_session_ids_namespace_not_found(self, claudecowork_sync):
        """Test that missing namespace returns empty set."""
        from kaizen.schema.exceptions import NamespaceNotFoundException

        claudecowork_sync.client.search_entities.side_effect = (
            NamespaceNotFoundException()
        )

        result = claudecowork_sync._get_processed_session_ids()

        assert result == set()


# =============================================================================
# Read Audit Log Tests
# =============================================================================


@pytest.mark.unit
class TestReadAuditLog:
    """Tests for _read_audit_log method."""

    def test_read_audit_log_success(self, claudecowork_sync, sample_session):
        """Test reading audit log successfully."""
        session = ClaudeCoworkSession(
            session_id=sample_session["session_id"],
            session_dir=sample_session["session_dir"],
            metadata_file=sample_session["metadata_file"],
            audit_file=sample_session["audit_file"],
        )

        events = claudecowork_sync._read_audit_log(session)

        assert len(events) == 4
        assert events[0]["type"] == "user"
        assert events[1]["type"] == "system"
        assert events[2]["type"] == "assistant"
        assert events[3]["type"] == "result"

    def test_read_audit_log_nonexistent_file(self, claudecowork_sync, temp_sessions_dir):
        """Test reading non-existent audit file."""
        session = ClaudeCoworkSession(
            session_id="nonexistent",
            session_dir=temp_sessions_dir / "nonexistent",
            metadata_file=temp_sessions_dir / "nonexistent.json",
            audit_file=temp_sessions_dir / "nonexistent" / "audit.jsonl",
        )

        events = claudecowork_sync._read_audit_log(session)

        assert events == []
