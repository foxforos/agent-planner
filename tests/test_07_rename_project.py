import planner
from planner import Planner
from models import Project
from datetime import datetime
import pytest


def make_project(name: str, filename: str) -> Project:
    return Project(
        name=name,
        objective="Test objective",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        filename=filename,
        tags=[],
        format="md",
    )


def test_rename_project_returns_report_if_not_found(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    result = p.rename_project("Missing", "Beta")

    assert isinstance(result, dict)
    assert result["found"] is False


def test_rename_project_returns_error_in_report_if_new_name_already_exists(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [
        make_project("Alpha", "alpha.md"),
        make_project("Beta", "beta.md"),
    ]

    result = p.rename_project("Alpha", "Beta")

    assert isinstance(result, dict)
    assert "Nome progetto già esistente" in result["error"]


def test_rename_project_updates_memory_renames_file_and_calls_save_memory(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    old_file = tmp_docs / "alpha.md"
    old_file.write_text("Some content", encoding="utf-8")

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Alpha", "alpha.md")]

    calls = {"count": 0}

    def fake_save_memory():
        calls["count"] += 1

    monkeypatch.setattr(p, "save_memory", fake_save_memory)

    result = p.rename_project("Alpha", "Beta")

    assert result["renamed_memory"] is True
    assert result["renamed_file"] is True
    assert p.memory[0].name == "Beta"
    assert p.memory[0].filename == "progetto_Beta.md"
    assert calls["count"] == 1
    assert not old_file.exists()
    assert (tmp_docs / "progetto_Beta.md").exists()
