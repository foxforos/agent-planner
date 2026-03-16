from datetime import datetime

from models import Project
from planner import Planner


def make_project(name: str, tags: list[str]) -> Project:
    return Project(
        name=name,
        objective="Test objective",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        filename=f"{name}.md",
        tags=tags,
        format="md",
    )


def test_add_tags_to_project_normalizes_tags_and_does_not_add_duplicates(tmp_path, monkeypatch):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Alpha", ["python"])]

    calls = {"count": 0}

    def fake_save_memory():
        calls["count"] += 1

    monkeypatch.setattr(p, "save_memory", fake_save_memory)

    added = p.add_tags_to_project("Alpha", ["  Python  ", "Video Editing", "video editing", "AI "])

    assert added == ["video-editing", "ai"]
    assert p.memory[0].tags == ["python", "video-editing", "ai"]
    assert calls["count"] == 1


def test_remove_tags_from_project_is_idempotent(tmp_path, monkeypatch):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Alpha", ["python", "video-editing"])]

    calls = {"count": 0}

    def fake_save_memory():
        calls["count"] += 1

    monkeypatch.setattr(p, "save_memory", fake_save_memory)

    removed = p.remove_tags_from_project("Alpha", ["  Python  ", "missing-tag"])

    assert removed == ["python"]
    assert p.memory[0].tags == ["video-editing"]
    assert calls["count"] == 1


def test_filter_projects_by_tags_returns_only_projects_matching_all_tags(tmp_path):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [
        make_project("Alpha", ["python", "ai"]),
        make_project("Beta", ["python"]),
        make_project("Gamma", ["ai"]),
    ]

    result = p.filter_projects_by_tags([" Python ", "AI"])

    assert len(result) == 1
    assert result[0].name == "Alpha"


def test_add_tags_to_project_returns_none_if_project_not_found(tmp_path, monkeypatch):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    calls = {"count": 0}

    def fake_save_memory():
        calls["count"] += 1

    monkeypatch.setattr(p, "save_memory", fake_save_memory)

    added = p.add_tags_to_project("Missing", ["python"])

    assert added is None
    assert calls["count"] == 0


def test_remove_tags_from_project_returns_empty_list_if_no_valid_tags(tmp_path, monkeypatch):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Alpha", ["python"])]

    calls = {"count": 0}

    def fake_save_memory():
        calls["count"] += 1

    monkeypatch.setattr(p, "save_memory", fake_save_memory)

    removed = p.remove_tags_from_project("Alpha", ["   ", ""])

    assert removed == []
    assert p.memory[0].tags == ["python"]
    assert calls["count"] == 0