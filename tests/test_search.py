from pathlib import Path

from app.services.indexer import init_db
from app.services.searcher import search


def test_search_returns_hits(tmp_path: Path):
    db_path = tmp_path / "kb.sqlite"
    init_db(db_path)

    import sqlite3

    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO documents (html_path, pdf_path, sha256, extracted_text, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("/tmp/a.html", "/tmp/a.pdf", "abc", "alpha beta gamma", "now"),
        )
        doc_id = cur.lastrowid
        conn.execute(
            "INSERT INTO documents_fts (rowid, extracted_text) VALUES (?, ?)",
            (doc_id, "alpha beta gamma"),
        )
        conn.commit()

    results = search(db_path, "alpha")
    assert len(results) == 1
    assert results[0]["doc_id"] == 1
