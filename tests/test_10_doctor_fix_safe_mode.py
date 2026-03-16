import json
from datetime import datetime

import planner
from planner import Planner
from models import Project


def make_project(name: str, filename: str, format: str = "md") -> Project:
    return Project(
        name=name,
        objective="Test objective",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        filename=filename,
        tags=[],
        format=format,
    )


def test_doctor_fix_returns_empty_summary_if_no_issues(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    memory_path = tmp_path / "memory.json"

    p = Planner(memory_path=str(memory_path))
    p.memory = [make_project("Alpha", "alpha.md")]
    p.save_memory()

    (tmp_docs / "alpha.md").write_text("content", encoding="utf-8")

    result = p.doctor_fix()

    assert result == {
        "removed_records": [],
        "moved_files": [],
        "backup_path": None,
    }
    assert len(p.memory) == 1
    assert p.memory[0].name == "Alpha"
    assert (tmp_docs / "alpha.md").exists()
    assert not (tmp_docs / "_orphaned").exists()
    assert not (tmp_path / "backups").exists()


def test_doctor_fix_with_confirm_no_makes_no_changes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))
    monkeypatch.setattr("builtins.input", lambda _: "n")

    memory_path = tmp_path / "memory.json"

    p = Planner(memory_path=str(memory_path))
    p.memory = [
        make_project("Broken", "broken.txt", format="md"),
    ]
    p.save_memory()

    (tmp_docs / "broken.txt").write_text("broken content", encoding="utf-8")
    (tmp_docs / "orphan.md").write_text("orphan file", encoding="utf-8")

    result = p.doctor_fix()

    assert result == {
        "removed_records": [],
        "moved_files": [],
        "backup_path": None,
    }
    assert len(p.memory) == 1
    assert p.memory[0].name == "Broken"
    assert (tmp_docs / "broken.txt").exists()
    assert (tmp_docs / "orphan.md").exists()
    assert not (tmp_docs / "_orphaned").exists()
    assert not (tmp_path / "backups").exists()


def test_doctor_fix_with_confirm_yes_creates_backup_removes_invalid_records_and_moves_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))
    monkeypatch.setattr("builtins.input", lambda _: "y")

    memory_path = tmp_path / "memory.json"

    p = Planner(memory_path=str(memory_path))
    p.memory = [
        make_project("Broken", "broken.txt", format="md"),
        make_project("Valid", "valid.md", format="md"),
    ]
    p.save_memory()

    (tmp_docs / "broken.txt").write_text("broken content", encoding="utf-8")
    (tmp_docs / "valid.md").write_text("valid content", encoding="utf-8")
    (tmp_docs / "orphan.md").write_text("orphan file", encoding="utf-8")

    original_memory_raw = memory_path.read_text(encoding="utf-8")

    result = p.doctor_fix()

    assert result["removed_records"] == ["Broken"]
    assert set(result["moved_files"]) == {"broken.txt", "orphan.md"}    # set è un metodo di organizzazione dei dati che non permette la ripetizione di elementi uguali(in questo caso non c interessa l'ordine degli elementi nella lista)
    assert result["backup_path"] is not None

    backup_path = tmp_path / result["backup_path"]
    assert backup_path.exists()
    assert backup_path.read_text(encoding="utf-8") == original_memory_raw

    assert len(p.memory) == 1
    assert p.memory[0].name == "Valid"

    saved_data = json.loads(memory_path.read_text(encoding="utf-8"))
    assert len(saved_data) == 1
    assert saved_data[0]["name"] == "Valid"

    assert not (tmp_docs / "broken.txt").exists()
    assert not (tmp_docs / "orphan.md").exists()
    assert (tmp_docs / "valid.md").exists()

    assert (tmp_docs / "_orphaned" / "broken.txt").exists()
    assert (tmp_docs / "_orphaned" / "orphan.md").exists()