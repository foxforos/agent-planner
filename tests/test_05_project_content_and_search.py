from datetime import datetime

import planner
from models import Project
from planner import Planner


def make_project(name: str, filename: str) -> Project:
    return Project(
        name=name,
        objective="Test objective",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        filename=filename,
        tags=[],
        format="md",
    )


def test_get_project_content_returns_none_if_project_not_found(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    result = p.get_project_content("Missing Project")

    assert result is None


def test_get_project_content_returns_none_if_file_missing(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Alpha", "alpha.md")]

    result = p.get_project_content("Alpha")

    assert result is None


def test_get_project_content_returns_content_if_file_exists(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    file_path = tmp_docs / "alpha.md"
    file_path.write_text("Hello from file", encoding="utf-8")

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Alpha", "alpha.md")]

    result = p.get_project_content("Alpha")

    assert result == "Hello from file"


def test_search_finds_project_by_name(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Video Editing", "video_editing.md")]

    result = p.search("video")

    assert len(result) == 1
    assert result[0].name == "Video Editing"


def test_search_finds_project_by_content(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    file_path = tmp_docs / "alpha.md"
    file_path.write_text("This project talks about SEO strategy", encoding="utf-8")

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Alpha", "alpha.md")]

    result = p.search("seo")

    assert len(result) == 1
    assert result[0].name == "Alpha"