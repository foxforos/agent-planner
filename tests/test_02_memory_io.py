# tests/test_02_memory_io.py
from datetime import datetime
import json

from planner import Planner
from models import Project


def test_load_memory_file_not_found_returns_empty_list(tmp_path):
    memory_path = tmp_path / "missing_memory.json"

    p = Planner(memory_path=str(memory_path))

    assert p.memory == []


def test_load_memory_invalid_json_returns_empty_list(tmp_path):
    memory_path = tmp_path / "memory.json"
    memory_path.write_text("{ NOT JSON }", encoding="utf-8")

    p = Planner(memory_path=str(memory_path))

    assert p.memory == []


def test_save_memory_writes_valid_json(tmp_path):
    memory_path = tmp_path / "memory.json"

    p = Planner(memory_path=str(memory_path))
    assert p.memory == []

    project = Project(
        name="Test Project",
        objective="Test objective",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        filename="docs/test_project.md",
        tags=["test", "pytest"],
        format="md",
    )

    p.memory = [project]
    p.save_memory()

    raw = memory_path.read_text(encoding="utf-8")
    data = json.loads(raw)

    assert isinstance(data, list)
    assert len(data) == 1

    item = data[0]
    assert item["name"] == "Test Project"
    assert item["objective"] == "Test objective"
    assert item["filename"] == "docs/test_project.md"
    assert item["format"] == "md"
    assert item["tags"] == ["test", "pytest"]

    # created_at deve essere serializzato (tipicamente ISO string)
    assert "created_at" in item
    assert isinstance(item["created_at"], str)
    assert item["created_at"].startswith("2026-01-01")