from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.services.converter import html_to_pdf
from app.services.extractor import extract_text


@dataclass
class IngestStats:
    processed: int
    updated: int
    skipped: int
    removed: int


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                html_path TEXT UNIQUE NOT NULL,
                pdf_path TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
            USING fts5(extracted_text, content='documents', content_rowid='id')
            """
        )


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _upsert_document(
    conn: sqlite3.Connection,
    *,
    html_path: Path,
    pdf_path: Path,
    sha256: str,
    extracted_text: str,
) -> bool:
    cur = conn.execute(
        "SELECT id, sha256 FROM documents WHERE html_path = ?", (str(html_path),)
    )
    row = cur.fetchone()
    updated_at = datetime.now(timezone.utc).isoformat()

    if row is not None and row[1] == sha256:
        return False

    if row is None:
        cur = conn.execute(
            """
            INSERT INTO documents (html_path, pdf_path, sha256, extracted_text, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(html_path), str(pdf_path), sha256, extracted_text, updated_at),
        )
        doc_id = cur.lastrowid
    else:
        doc_id = row[0]
        conn.execute(
            """
            UPDATE documents
            SET pdf_path = ?, sha256 = ?, extracted_text = ?, updated_at = ?
            WHERE id = ?
            """,
            (str(pdf_path), sha256, extracted_text, updated_at, doc_id),
        )
        conn.execute("DELETE FROM documents_fts WHERE rowid = ?", (doc_id,))

    conn.execute(
        "INSERT INTO documents_fts (rowid, extracted_text) VALUES (?, ?)",
        (doc_id, extracted_text),
    )
    return True


def _remove_missing(conn: sqlite3.Connection, existing: set[str]) -> int:
    cur = conn.execute("SELECT id, html_path FROM documents")
    removed = 0
    for doc_id, html_path in cur.fetchall():
        if html_path not in existing:
            conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.execute("DELETE FROM documents_fts WHERE rowid = ?", (doc_id,))
            removed += 1
    return removed


def ingest_html_folder(html_root: Path, pdf_root: Path, db_path: Path) -> IngestStats:
    init_db(db_path)
    html_files = sorted(
        [p for p in html_root.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".htm"}]
    )
    existing = {str(p) for p in html_files}

    processed = updated = skipped = 0

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        for html_path in html_files:
            rel_path = html_path.relative_to(html_root)
            pdf_path = (pdf_root / rel_path).with_suffix(".pdf")

            sha256 = _sha256(html_path)
            cur = conn.execute(
                "SELECT sha256 FROM documents WHERE html_path = ?", (str(html_path),)
            )
            row = cur.fetchone()
            if row is not None and row[0] == sha256:
                skipped += 1
                processed += 1
                continue

            html_to_pdf(html_path, pdf_path)
            html_text = html_path.read_text(encoding="utf-8", errors="ignore")
            extracted = extract_text(html_text)

            if _upsert_document(
                conn,
                html_path=html_path,
                pdf_path=pdf_path,
                sha256=sha256,
                extracted_text=extracted,
            ):
                updated += 1
            processed += 1

        removed = _remove_missing(conn, existing)
        conn.commit()

    return IngestStats(processed=processed, updated=updated, skipped=skipped, removed=removed)
