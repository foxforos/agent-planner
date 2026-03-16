import planner
import pytest
from planner import Planner


def test_generate_plan_raises_file_not_found_if_template_missing(tmp_path, monkeypatch):
    tmp_base = tmp_path / "fake_project"
    tmp_base.mkdir()

    templates_dir = tmp_base / "templates"
    templates_dir.mkdir()

    monkeypatch.setattr(planner, "__file__", str(tmp_base / "planner.py"))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    with pytest.raises(FileNotFoundError):
        p.generate_plan(objective="Imparare pytest", template_name="missing_template")


def test_generate_plan_raises_value_error_if_template_is_empty(tmp_path, monkeypatch):
    tmp_base = tmp_path / "fake_project"
    tmp_base.mkdir()

    templates_dir = tmp_base / "templates"
    templates_dir.mkdir()

    empty_template = templates_dir / "empty.txt"
    empty_template.write_text("", encoding="utf-8")

    monkeypatch.setattr(planner, "__file__", str(tmp_base / "planner.py"))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    with pytest.raises(ValueError):
        p.generate_plan(objective="Imparare pytest", template_name="empty")


def test_generate_plan_raises_value_error_if_template_has_invalid_placeholder(tmp_path, monkeypatch):
    tmp_base = tmp_path / "fake_project"
    tmp_base.mkdir()

    templates_dir = tmp_base / "templates"
    templates_dir.mkdir()

    bad_template = templates_dir / "bad.txt"
    bad_template.write_text("Obiettivo: {objectiv}", encoding="utf-8")

    monkeypatch.setattr(planner, "__file__", str(tmp_base / "planner.py"))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    with pytest.raises(ValueError):
        p.generate_plan(objective="Imparare pytest", template_name="bad")


def test_generate_plan_happy_path_renders_prompt_calls_openai_and_returns_content(tmp_path, monkeypatch):
    tmp_base = tmp_path / "fake_project"
    tmp_base.mkdir()

    templates_dir = tmp_base / "templates"
    templates_dir.mkdir()

    default_template = templates_dir / "default.txt"
    default_template.write_text(
        "Crea un piano dettagliato per il seguente obiettivo: {objective}",
        encoding="utf-8",
    )

    monkeypatch.setattr(planner, "__file__", str(tmp_base / "planner.py"))
    monkeypatch.setattr(planner, "require_openai_api_key", lambda: "fake-api-key")

    calls = {}

    class FakeOpenAI:
        def __init__(self, api_key):
            calls["api_key"] = api_key
            self.chat = self.Chat()

        class Chat:
            def __init__(self):
                self.completions = self.Completions()

            class Completions:
                def create(self, model, messages):
                    calls["model"] = model
                    calls["messages"] = messages

                    class FakeMessage:
                        content = "PIANO GENERATO FAKE"

                    class FakeChoice:
                        message = FakeMessage()

                    class FakeResponse:
                        choices = [FakeChoice()]

                    return FakeResponse()

    monkeypatch.setattr(planner, "OpenAI", FakeOpenAI)

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    result = p.generate_plan(objective="Imparare pytest", template_name="default")

    assert result == "PIANO GENERATO FAKE"
    assert calls["api_key"] == "fake-api-key"
    assert calls["model"] == planner.MODEL
    assert calls["messages"] == [
        {
            "role": "user",
            "content": "Crea un piano dettagliato per il seguente obiettivo: Imparare pytest",
        }
    ]