import planner
from planner import Planner
from models import Project
from datetime import datetime


def make_project(name: str, filename: str) -> Project:
    return Project(
        name=name,
        objective="Test objective",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        filename=filename,
        tags=[],
        format="md",
    )


def test_delete_project_returns_report_if_not_found(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    result = p.delete_project("Missing")

    assert result["found"] is False
    assert result["name"] == "Missing"
    assert result["filename"] is None
    assert result["filepath"] is None
    assert result["will_delete_memory"] is False
    assert result["will_delete_file"] is False
    assert result["deleted_memory"] is False
    assert result["deleted_file"] is False


def test_delete_project_removes_project_and_file(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()

    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    file_path = tmp_docs / "alpha.md"
    file_path.write_text("Some content", encoding="utf-8")

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Alpha", "alpha.md")]

    calls = {"count": 0}

    def fake_save_memory():
        calls["count"] += 1

    monkeypatch.setattr(p, "save_memory", fake_save_memory)

    result = p.delete_project("Alpha")

    assert result["found"] is True
    assert result["name"] == "Alpha"
    assert result["filename"] == "alpha.md"
    assert result["filepath"] == str(file_path)
    assert result["will_delete_memory"] is True
    assert result["will_delete_file"] is True
    assert result["deleted_memory"] is True
    assert result["deleted_file"] is True

    assert len(p.memory) == 0
    assert calls["count"] == 1
    assert not file_path.exists()


def test_delete_project_dry_run_returns_preview_without_modifying_state(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()

    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    file_path = tmp_docs / "alpha.md"
    file_path.write_text("Some content", encoding="utf-8")

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Alpha", "alpha.md")]

    calls = {"count": 0}

    def fake_save_memory():
        calls["count"] += 1

    monkeypatch.setattr(p, "save_memory", fake_save_memory)

    result = p.delete_project("Alpha", dry_run=True)

    assert result["found"] is True
    assert result["name"] == "Alpha"
    assert result["filename"] == "alpha.md"
    assert result["filepath"] == str(file_path)
    assert result["will_delete_memory"] is True
    assert result["will_delete_file"] is True
    assert result["deleted_memory"] is False
    assert result["deleted_file"] is False

    assert len(p.memory) == 1
    assert p.memory[0].name == "Alpha"
    assert calls["count"] == 0
    assert file_path.exists()