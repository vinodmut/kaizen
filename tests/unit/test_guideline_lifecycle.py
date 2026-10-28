"""Guideline adoption lifecycle: candidate -> active -> retired, without deleting anything."""

from datetime import UTC, datetime

import pytest
from typer.testing import CliRunner

from altk_evolve.backend.reconciliation import existing_memory_metadata
from altk_evolve.cli.cli import app
from altk_evolve.config.evolve import EvolveConfig
from altk_evolve.config.filesystem import FilesystemSettings
from altk_evolve.frontend.client.evolve_client import EvolveClient
from altk_evolve.schema.conflict_resolution import EntityUpdate
from altk_evolve.schema.core import Entity, RecordedEntity
from altk_evolve.schema.exceptions import EvolveException
from altk_evolve.schema.lifecycle import filter_by_status, set_guideline_status, status_of

pytestmark = pytest.mark.unit
OBSERVED = datetime(2026, 10, 28, tzinfo=UTC)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("EVOLVE_HOOKS_CONFIG", "")
    client = EvolveClient(EvolveConfig(settings=FilesystemSettings(data_dir=str(tmp_path / "entities"))))
    client.create_namespace("ns")
    return client


def _add(client, content, **metadata):
    [update] = client.update_entities(
        "ns", [Entity(type="guideline", content=content, metadata=metadata)], enable_conflict_resolution=False
    )
    return update.id


def test_missing_status_counts_as_active():
    assert status_of(Entity(type="guideline", content="x")) == "active"
    assert status_of(Entity(type="guideline", content="x", metadata={"status": "bogus"})) == "active"
    assert status_of(Entity(type="guideline", content="x", metadata={"status": "candidate"})) == "candidate"


def test_filter_by_status_rejects_unknown_status():
    with pytest.raises(EvolveException, match="Unknown guideline status"):
        filter_by_status([], {"pending"})


def test_promote_then_retire_keeps_entity_and_history(client):
    entity_id = _add(client, "Run the tests before committing", status="candidate")

    set_guideline_status(client, "ns", entity_id, "active", by="alice", reason="useful", now=OBSERVED)
    set_guideline_status(client, "ns", entity_id, "retired", by="bob", reason="stale", now=OBSERVED)

    entity = client.get_entity_by_id("ns", entity_id)
    assert entity is not None and entity.content == "Run the tests before committing"
    assert entity.metadata["status"] == "retired"
    assert [(h["from"], h["to"], h["by"], h["reason"]) for h in entity.metadata["status_history"]] == [
        ("candidate", "active", "alice", "useful"),
        ("active", "retired", "bob", "stale"),
    ]


def test_setting_the_current_status_is_a_no_op(client):
    entity_id = _add(client, "x", status="active")
    set_guideline_status(client, "ns", entity_id, "active")
    assert "status_history" not in client.get_entity_by_id("ns", entity_id).metadata


def test_status_change_requires_an_existing_guideline(client):
    with pytest.raises(EvolveException, match="not found"):
        set_guideline_status(client, "ns", "missing", "active")
    [fact] = client.update_entities("ns", [Entity(type="fact", content="f")], enable_conflict_resolution=False)
    with pytest.raises(EvolveException, match="not a guideline"):
        set_guideline_status(client, "ns", fact.id, "active")


def test_select_guidelines_filters_by_status(client):
    legacy = _add(client, "legacy guideline")
    active = _add(client, "active guideline", status="active")
    _add(client, "candidate guideline", status="candidate")
    _add(client, "retired guideline", status="retired")

    selected = client.select_guidelines("ns", "anything", top_k=10, core_support=99, statuses={"active"})
    assert {e.id for e in selected.all} == {legacy, active}
    assert len(client.select_guidelines("ns", "anything", top_k=10, core_support=99).all) == 4


@pytest.mark.parametrize("stored_status", ["active", "retired"])
def test_conflict_update_keeps_stored_lifecycle(stored_status):
    history = [{"from": "candidate", "to": stored_status}]
    old = RecordedEntity(
        id="1", type="guideline", content="old", created_at=OBSERVED, metadata={"status": stored_status, "status_history": history}
    )
    incoming = RecordedEntity(id="in", type="guideline", content="new", created_at=OBSERVED, metadata={"status": "candidate"})
    decision = EntityUpdate(id="1", type="guideline", content="merged", event="UPDATE", incoming_ids=["in"])

    metadata = existing_memory_metadata(decision, old, [incoming], False, OBSERVED)

    assert metadata["status"] == stored_status
    assert metadata["status_history"] == history


def test_conflict_update_of_legacy_memory_stays_unset():
    old = RecordedEntity(id="1", type="guideline", content="old", created_at=OBSERVED, metadata={})
    incoming = RecordedEntity(id="in", type="guideline", content="new", created_at=OBSERVED, metadata={"status": "candidate"})
    decision = EntityUpdate(id="1", type="guideline", content="merged", event="UPDATE", incoming_ids=["in"])
    assert "status" not in existing_memory_metadata(decision, old, [incoming], False, OBSERVED)


def test_cli_promote_retire_and_list_by_status(client, monkeypatch):
    monkeypatch.setattr("altk_evolve.cli.cli.get_client", lambda: client)
    entity_id = _add(client, "candidate guideline", status="candidate")
    runner = CliRunner()

    listed = runner.invoke(app, ["entities", "list", "ns", "--status", "candidate"])
    assert listed.exit_code == 0 and entity_id in listed.output

    promoted = runner.invoke(app, ["entities", "promote", "ns", entity_id, "--reason", "ok"])
    assert promoted.exit_code == 0, promoted.output
    assert status_of(client.get_entity_by_id("ns", entity_id)) == "active"
    assert "No entities" in runner.invoke(app, ["entities", "list", "ns", "--status", "candidate"]).output

    assert runner.invoke(app, ["entities", "retire", "ns", entity_id]).exit_code != 0  # --reason is required
    retired = runner.invoke(app, ["entities", "retire", "ns", entity_id, "--reason", "stale"])
    assert retired.exit_code == 0, retired.output
    assert status_of(client.get_entity_by_id("ns", entity_id)) == "retired"

    assert runner.invoke(app, ["entities", "promote", "ns", "missing"]).exit_code == 1
