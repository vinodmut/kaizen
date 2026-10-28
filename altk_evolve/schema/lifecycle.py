"""Guideline adoption lifecycle: candidate -> active -> retired, kept in entity metadata.

A guideline without ``metadata.status`` predates the lifecycle and is treated as active, so
existing stores keep serving what they served. Untrusted sources (for example Cortex session
ingestion) write ``status: candidate``; a reviewer promotes it before consumers that ask for
active guidelines will see it. Retiring keeps the entity and its history instead of deleting it.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal, get_args

from altk_evolve.schema.core import Entity
from altk_evolve.schema.exceptions import EvolveException

if TYPE_CHECKING:
    from altk_evolve.frontend.client.evolve_client import EvolveClient
    from altk_evolve.schema.core import RecordedEntity

GuidelineStatus = Literal["candidate", "active", "retired"]
STATUSES: frozenset[str] = frozenset(get_args(GuidelineStatus))
DEFAULT_STATUS: GuidelineStatus = "active"
# Metadata keys the lifecycle owns; reconciliation keeps the stored values.
LIFECYCLE_KEYS = ("status", "status_history")


def status_of(entity: Entity) -> str:
    """The entity's lifecycle status, treating a missing status as active."""
    value = (entity.metadata or {}).get("status")
    return value if isinstance(value, str) and value in STATUSES else DEFAULT_STATUS


def filter_by_status(entities: list["RecordedEntity"], statuses: set[str] | frozenset[str] | None) -> list["RecordedEntity"]:
    """Keep entities whose status is in ``statuses``; ``None`` keeps everything."""
    if statuses is None:
        return entities
    unknown = set(statuses) - STATUSES
    if unknown:
        raise EvolveException(f"Unknown guideline status: {', '.join(sorted(unknown))}")
    return [entity for entity in entities if status_of(entity) in statuses]


def set_guideline_status(
    client: "EvolveClient",
    namespace_id: str,
    entity_id: str,
    to: GuidelineStatus,
    *,
    by: str | None = None,
    reason: str | None = None,
    now: datetime | None = None,
) -> "RecordedEntity":
    """Move a guideline to ``to`` and append the transition to ``status_history``."""
    if to not in STATUSES:
        raise EvolveException(f"Unknown guideline status: {to}")
    entity = client.get_entity_by_id(namespace_id, entity_id)
    if entity is None:
        raise EvolveException(f"Entity {entity_id} not found")
    if entity.type != "guideline":
        raise EvolveException(f"Entity {entity_id} is a {entity.type}, not a guideline")
    current = status_of(entity)
    if current == to:
        return entity
    history = list((entity.metadata or {}).get("status_history") or [])
    history.append(
        {
            "from": current,
            "to": to,
            "at": (now or datetime.now(UTC)).isoformat(),
            "by": by,
            "reason": reason,
        }
    )
    return client.patch_entity_metadata(namespace_id, entity_id, {"status": to, "status_history": history})
