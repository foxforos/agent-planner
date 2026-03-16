import doc_builder


def test_save_markdown_creates_docs_folder_and_writes_file(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    monkeypatch.setattr(doc_builder, "DOCS_FOLDER", str(tmp_docs))

    result = doc_builder.save_markdown("test_file.md", "# Hello Markdown")

    assert tmp_docs.exists()
    assert tmp_docs.is_dir()
    assert (tmp_docs / "test_file.md").exists()
    assert (tmp_docs / "test_file.md").read_text(encoding="utf-8") == "# Hello Markdown"
    assert result == str(tmp_docs / "test_file.md")


def test_save_text_creates_docs_folder_and_writes_file(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    monkeypatch.setattr(doc_builder, "DOCS_FOLDER", str(tmp_docs))

    result = doc_builder.save_text("note.txt", "Hello text file")

    assert tmp_docs.exists()
    assert tmp_docs.is_dir()
    assert (tmp_docs / "note.txt").exists()
    assert (tmp_docs / "note.txt").read_text(encoding="utf-8") == "Hello text file"
    assert result == str(tmp_docs / "note.txt")


def test_ensure_docs_folder_creates_folder_if_missing(tmp_path, monkeypatch):
    tmp_docs = tmp_path / "docs"
    monkeypatch.setattr(doc_builder, "DOCS_FOLDER", str(tmp_docs))

    assert not tmp_docs.exists()

    doc_builder.ensure_docs_folder()

    assert tmp_docs.exists()
    assert tmp_docs.is_dir()