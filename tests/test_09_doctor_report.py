import planner
from planner import Planner
from models import Project
from datetime import datetime


def make_project(name: str, filename: str, format: str = "md") -> Project:
    return Project(
        name=name,
        objective="Test objective",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        filename=filename,
        tags=[],
        format=format,
    )


def test_doctor_report_detects_missing_files(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [
        make_project("Alpha", "alpha.md"),
    ]

    report = p.doctor_report()

    assert report["missing_files"] == ["Alpha"]
    assert report["orphan_files"] == []
    assert report["invalid_records"] == []
    assert report["duplicate_names"] == []
    assert report["duplicate_filenames"] == []


def test_doctor_report_detects_orphan_files(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    (tmp_docs / "orphan.md").write_text("orphan file", encoding="utf-8")

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    report = p.doctor_report()

    assert report["missing_files"] == []
    assert report["orphan_files"] == ["orphan.md"]
    assert report["invalid_records"] == []
    assert report["duplicate_names"] == []
    assert report["duplicate_filenames"] == []


def test_doctor_report_detects_invalid_records_for_extension_mismatch(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    (tmp_docs / "alpha.txt").write_text("content", encoding="utf-8")

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [
        make_project("Alpha", "alpha.txt", format="md"),
    ]

    report = p.doctor_report()

    assert report["missing_files"] == []
    assert report["orphan_files"] == []
    assert report["invalid_records"] == ["Alpha"]
    assert report["duplicate_names"] == []
    assert report["duplicate_filenames"] == []


def test_doctor_report_detects_duplicate_names_case_insensitive(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    (tmp_docs / "alpha.md").write_text("content", encoding="utf-8")
    (tmp_docs / "beta.md").write_text("content", encoding="utf-8")

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [
        make_project("Alpha", "alpha.md"),
        make_project(" alpha ", "beta.md"),
    ]

    report = p.doctor_report()

    assert report["missing_files"] == []
    assert report["orphan_files"] == []
    assert report["invalid_records"] == []
    assert report["duplicate_names"] == [" alpha "]
    assert report["duplicate_filenames"] == []


def test_doctor_report_detects_duplicate_filenames_case_insensitive(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    (tmp_docs / "alpha.md").write_text("content", encoding="utf-8")

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = [
        make_project("Alpha", "alpha.md"),
        make_project("Beta", " Alpha.md "),
    ]

    report = p.doctor_report()

    assert report["missing_files"] == ["Beta"]
    assert report["orphan_files"] == []
    assert report["invalid_records"] == ["Beta"]    # a causa di filename che finisce con "md " invece che con "md"
    assert report["duplicate_names"] == []
    assert report["duplicate_filenames"] == [" Alpha.md "]


def test_doctor_report_ignores_subdirectories_when_detecting_orphan_files(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    tmp_docs.mkdir()
    (tmp_docs / "_orphaned").mkdir()
    monkeypatch.setattr(planner, "DOCS_FOLDER", str(tmp_docs))

    p = Planner(memory_path=str(tmp_path / "memory.json"))
    p.memory = []

    report = p.doctor_report()

    assert report["missing_files"] == []
    assert report["orphan_files"] == []
    assert report["invalid_records"] == []
    assert report["duplicate_names"] == []
    assert report["duplicate_filenames"] == []