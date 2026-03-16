from planner import Planner
from models import Project


def make_project(name: str) -> Project:
    return Project(
        name=name,
        objective="Test objective",
        created_at="2026-01-01T12:00:00",
        filename=f"docs/{name}.md",
        tags=[],
        format="md",
    )


def test_get_unique_project_name_returns_same_name_if_not_exists(tmp_path):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    result = p.get_unique_project_name("Blog SEO")

    assert result == "Blog SEO"


def test_get_unique_project_name_returns_name_2_if_name_exists(tmp_path):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [make_project("Blog SEO")]

    result = p.get_unique_project_name("Blog SEO")

    assert result == "Blog SEO-2"


def test_get_unique_project_name_returns_next_available_suffix(tmp_path):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [
        make_project("Blog SEO"),
        make_project("Blog SEO-2"),
        make_project("Blog SEO-3"),
    ]

    result = p.get_unique_project_name("Blog SEO")

    assert result == "Blog SEO-4"


def test_get_unique_project_name_strips_spaces(tmp_path):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    result = p.get_unique_project_name("   Blog SEO   ")

    assert result == "Blog SEO"


def test_get_unique_project_name_returns_empty_string_if_name_is_only_spaces(tmp_path):
    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    result = p.get_unique_project_name("     ")

    assert result == ""