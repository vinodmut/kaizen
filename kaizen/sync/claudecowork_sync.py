"""
Claude Cowork Sync - Fetch trajectories from Claude Cowork local agent mode sessions.

This module provides functionality to:
1. Discover Claude Cowork sessions from local storage
2. Convert audit logs to OpenAI message format
3. Deduplicate already-processed trajectories
4. Generate tips/guidelines from new trajectories
5. Store both trajectories and tips in the Kaizen backend
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kaizen.config.claudecowork import claudecowork_settings
from kaizen.config.kaizen import kaizen_config
from kaizen.frontend.client.kaizen_client import KaizenClient
from kaizen.llm.tips.tips import generate_tips
from kaizen.schema.core import Entity
from kaizen.schema.exceptions import NamespaceNotFoundException
from kaizen.sync.phoenix_sync import SyncResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kaizen.sync.claudecowork")


@dataclass
class ClaudeCoworkSession:
    """Represents a discovered Claude Cowork session."""

    session_id: str
    session_dir: Path
    metadata_file: Path
    audit_file: Path
    title: str = ""
    model: str = ""
    created_at: int = 0
    last_activity_at: int = 0


class ClaudeCoworkSync:
    """Sync trajectories from Claude Cowork local agent mode sessions to Kaizen."""

    def __init__(
        self,
        sessions_dir: str | None = None,
        namespace_id: str | None = None,
    ):
        self.sessions_dir = Path(sessions_dir or claudecowork_settings.sessions_dir)
        self.namespace_id = namespace_id or kaizen_config.namespace_id
        self.client = KaizenClient()

    def _ensure_namespace(self):
        """Ensure the target namespace exists."""
        try:
            self.client.get_namespace_details(self.namespace_id)
        except NamespaceNotFoundException:
            self.client.create_namespace(self.namespace_id)
            logger.info(f"Created namespace: {self.namespace_id}")

    def _discover_sessions(self, limit: int = 100) -> list[ClaudeCoworkSession]:
        """
        Discover Claude Cowork sessions from the sessions directory.

        Sessions are stored in: {sessions_dir}/{uuid}/{uuid}/local_{session_id}/
        With metadata in: {sessions_dir}/{uuid}/{uuid}/local_{session_id}.json
        """
        sessions = []

        if not self.sessions_dir.exists():
            logger.warning(f"Sessions directory does not exist: {self.sessions_dir}")
            return sessions

        # Traverse the nested structure
        for uuid1_dir in self.sessions_dir.iterdir():
            if not uuid1_dir.is_dir() or uuid1_dir.name.startswith('.'):
                continue

            for uuid2_dir in uuid1_dir.iterdir():
                if not uuid2_dir.is_dir() or uuid2_dir.name.startswith('.'):
                    continue

                # Look for local_* directories and their sibling metadata files
                for item in uuid2_dir.iterdir():
                    if item.is_dir() and item.name.startswith('local_'):
                        session_id = item.name[6:]  # Remove 'local_' prefix
                        audit_file = item / 'audit.jsonl'
                        metadata_file = uuid2_dir / f"{item.name}.json"

                        if audit_file.exists():
                            session = ClaudeCoworkSession(
                                session_id=session_id,
                                session_dir=item,
                                metadata_file=metadata_file,
                                audit_file=audit_file,
                            )

                            # Load metadata if available
                            if metadata_file.exists():
                                try:
                                    with open(metadata_file) as f:
                                        meta = json.load(f)
                                    session.title = meta.get('title', '')
                                    session.model = meta.get('model', '')
                                    session.created_at = meta.get('createdAt', 0)
                                    session.last_activity_at = meta.get(
                                        'lastActivityAt', 0
                                    )
                                except (json.JSONDecodeError, OSError) as e:
                                    logger.warning(
                                        f"Failed to read metadata for {session_id}: {e}"
                                    )

                            sessions.append(session)

        # Sort by last activity (most recent first) and limit
        sessions.sort(key=lambda s: s.last_activity_at, reverse=True)
        return sessions[:limit]

    def _get_processed_session_ids(self) -> set[str]:
        """Get session_ids that have already been processed."""
        try:
            entities = self.client.search_entities(
                namespace_id=self.namespace_id,
                filters={"type": "trajectory"},
                limit=10000,
            )
            return {
                e.metadata.get("session_id")
                for e in entities
                if e.metadata and e.metadata.get("session_id")
            }
        except NamespaceNotFoundException:
            return set()

    def _read_audit_log(self, session: ClaudeCoworkSession) -> list[dict]:
        """Read and parse the audit log for a session."""
        events = []
        try:
            with open(session.audit_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse audit line: {e}")
        except OSError as e:
            logger.error(f"Failed to read audit file {session.audit_file}: {e}")
        return events

    def _convert_audit_event_to_openai(
        self, event: dict
    ) -> dict | list[dict] | None:
        """
        Convert a Claude Cowork audit event to OpenAI message format.

        Returns:
            - A single message dict
            - A list of message dicts (for tool results)
            - None if the event should be skipped
        """
        event_type = event.get("type")

        if event_type == "system":
            # Skip system init events
            return None

        if event_type == "result":
            # Skip result events (usage stats are handled separately)
            return None

        if event_type == "user":
            message = event.get("message", {})
            content = message.get("content")

            if isinstance(content, str):
                # Simple user message
                return {"role": "user", "content": content}

            if isinstance(content, list):
                # Check for tool_result blocks
                tool_results = []
                text_parts = []

                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "tool_result":
                            tool_results.append({
                                "role": "tool",
                                "tool_call_id": block.get("tool_use_id", ""),
                                "content": self._extract_tool_result_content(
                                    block.get("content", "")
                                ),
                            })
                        elif block.get("type") == "text":
                            text_parts.append(block.get("text", ""))

                if tool_results:
                    return tool_results

                if text_parts:
                    return {"role": "user", "content": "\n\n".join(text_parts)}

            return None

        if event_type == "assistant":
            message = event.get("message", {})
            content = message.get("content", [])

            # Handle string content directly
            if isinstance(content, str):
                return {"role": "assistant", "content": content}

            text_parts = []
            thinking_parts = []
            tool_calls = []

            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue

                    block_type = block.get("type")

                    if block_type == "text":
                        text = block.get("text", "")
                        if text and text != "(no content)":
                            text_parts.append(text)

                    elif block_type == "thinking":
                        thinking = block.get("thinking", "")
                        if thinking:
                            thinking_parts.append(thinking)

                    elif block_type == "tool_use":
                        tool_calls.append({
                            "id": block.get("id", ""),
                            "type": "function",
                            "function": {
                                "name": block.get("name", ""),
                                "arguments": json.dumps(block.get("input", {})),
                            },
                        })

            result = {"role": "assistant"}

            if thinking_parts:
                result["thinking"] = "\n\n".join(thinking_parts)

            if text_parts:
                result["content"] = "\n\n".join(text_parts)
            elif not tool_calls:
                result["content"] = None

            if tool_calls:
                result["tool_calls"] = tool_calls

            return result

        return None

    def _extract_tool_result_content(self, content: Any) -> str:
        """Extract string content from tool result."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            # Handle list of content blocks
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    text_parts.append(block)
            return "\n".join(text_parts)
        return str(content)

    def _extract_trajectory(
        self, audit_events: list[dict], session: ClaudeCoworkSession
    ) -> dict:
        """Extract a complete trajectory from audit events."""
        messages = []
        total_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_input_tokens": 0,
            "cache_creation_input_tokens": 0,
        }

        for event in audit_events:
            # Extract usage stats from result events
            if event.get("type") == "result":
                usage = event.get("usage", {})
                total_usage["input_tokens"] += usage.get("input_tokens", 0)
                total_usage["output_tokens"] += usage.get("output_tokens", 0)
                total_usage["cache_read_input_tokens"] += usage.get(
                    "cache_read_input_tokens", 0
                )
                total_usage["cache_creation_input_tokens"] += usage.get(
                    "cache_creation_input_tokens", 0
                )
                continue

            converted = self._convert_audit_event_to_openai(event)

            if converted is None:
                continue

            if isinstance(converted, list):
                messages.extend(converted)
            else:
                messages.append(converted)

        return {
            "session_id": session.session_id,
            "title": session.title,
            "model": session.model,
            "created_at": session.created_at,
            "last_activity_at": session.last_activity_at,
            "messages": messages,
            "usage": total_usage,
        }

    def _clean_trajectory(self, trajectory: dict) -> dict:
        """Clean up a trajectory by removing system reminders and empty messages."""
        cleaned_messages = []

        for msg in trajectory.get("messages", []):
            if not msg.get("content") and not msg.get("tool_calls"):
                continue

            if msg.get("content"):
                content = msg["content"]
                if isinstance(content, str):
                    # Remove system reminders
                    content = re.sub(
                        r"<system-reminder>.*?</system-reminder>",
                        "",
                        content,
                        flags=re.DOTALL,
                    ).strip()
                    if not content:
                        continue
                    msg = {**msg, "content": content}

            cleaned_messages.append(msg)

        return {**trajectory, "messages": cleaned_messages}

    def _process_trajectory(self, trajectory: dict) -> int:
        """
        Process a single trajectory: store it and generate tips.

        Returns the number of tips generated.
        """
        messages = trajectory.get("messages", [])
        if messages:
            entity = Entity(
                type="trajectory",
                content=messages,
                metadata={
                    "session_id": trajectory["session_id"],
                    "title": trajectory["title"],
                    "model": trajectory["model"],
                    "source": "claudecowork",
                    "created_at": trajectory["created_at"],
                    "last_activity_at": trajectory["last_activity_at"],
                    "message_count": len(messages),
                    "usage": trajectory.get("usage"),
                },
            )
            self.client.update_entities(
                namespace_id=self.namespace_id,
                entities=[entity],
                enable_conflict_resolution=False,
            )

        # Generate tips from the trajectory
        tips = generate_tips(trajectory["messages"])

        if tips:
            tip_entities = [
                Entity(
                    type="guideline",
                    content=tip.content,
                    metadata={
                        "category": tip.category,
                        "rationale": tip.rationale,
                        "trigger": tip.trigger,
                        "source_session_id": trajectory["session_id"],
                    },
                )
                for tip in tips
            ]
            self.client.update_entities(
                namespace_id=self.namespace_id,
                entities=tip_entities,
                enable_conflict_resolution=True,
            )

        return len(tips)

    def sync(
        self,
        limit: int = 100,
        include_errors: bool = False,
    ) -> SyncResult:
        """
        Fetch new trajectories from Claude Cowork sessions and generate tips.

        Args:
            limit: Maximum number of sessions to process
            include_errors: Whether to include sessions with errors (not used currently)

        Returns:
            SyncResult with counts of processed, skipped, and tips generated
        """
        logger.info(
            f"Starting sync from {self.sessions_dir} to namespace '{self.namespace_id}'"
        )

        self._ensure_namespace()

        # Discover sessions
        sessions = self._discover_sessions(limit)
        logger.info(f"Discovered {len(sessions)} sessions")

        # Get already processed session IDs
        processed_ids = self._get_processed_session_ids()
        logger.info(f"Found {len(processed_ids)} already processed sessions")

        processed = 0
        skipped = 0
        tips_generated = 0
        errors = []

        for session in sessions:
            # Check if already processed
            if session.session_id in processed_ids:
                skipped += 1
                continue

            try:
                # Read and convert audit log
                audit_events = self._read_audit_log(session)
                if not audit_events:
                    continue

                trajectory = self._extract_trajectory(audit_events, session)
                trajectory = self._clean_trajectory(trajectory)

                if trajectory["messages"]:
                    tips_count = self._process_trajectory(trajectory)
                    processed += 1
                    tips_generated += tips_count
                    logger.info(
                        f"Processed session {session.session_id[:12]}... - "
                        f"generated {tips_count} tips"
                    )
            except Exception as e:
                error_msg = f"Error processing session {session.session_id}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        result = SyncResult(
            processed=processed,
            skipped=skipped,
            tips_generated=tips_generated,
            errors=errors,
        )

        logger.info(
            f"Sync complete: {processed} processed, {skipped} skipped, "
            f"{tips_generated} tips generated, {len(errors)} errors"
        )

        return result
