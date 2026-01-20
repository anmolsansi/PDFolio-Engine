from __future__ import annotations

import sqlite3
from pathlib import Path


def _normalize_query(query: str) -> str:
    if '"' in query or "'" in query:
        return query
    tokens = [t for t in query.split() if t]
    if not tokens:
        return ""
    normalized = []
    for token in tokens:
        if token.endswith("*"):
            normalized.append(token)
        else:
            normalized.append(f"{token}*")
    return " ".join(normalized)


def search(db_path: Path, query: str, limit: int = 20, offset: int = 0) -> list[dict]:
    fts_query = _normalize_query(query)
    if not fts_query:
        return []

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            """
            SELECT d.id as doc_id,
                   d.html_path,
                   d.pdf_path,
                   bm25(documents_fts) as score,
                   snippet(documents_fts, 0, '[', ']', '...', 10) as snippet
            FROM documents_fts
            JOIN documents d ON documents_fts.rowid = d.id
            WHERE documents_fts MATCH ?
            ORDER BY score
            LIMIT ? OFFSET ?
            """,
            (fts_query, limit, offset),
        )
        return [dict(row) for row in cur.fetchall()]
