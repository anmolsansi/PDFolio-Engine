from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.config import load_config
from app.models.schema import SearchResponse, SearchResult
from app.services.searcher import search

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search_docs(q: str = Query("", min_length=1), limit: int = 20, offset: int = 0):
    config = load_config()
    results = search(config.index_db, q, limit=limit, offset=offset)
    mapped = [SearchResult(**row) for row in results]
    return SearchResponse(query=q, results=mapped)


@router.get("/download")
def download(doc_id: int):
    config = load_config()
    db_path = config.index_db

    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Index not found")

    from sqlite3 import connect

    with connect(db_path) as conn:
        cur = conn.execute(
            "SELECT pdf_path FROM documents WHERE id = ?",
            (doc_id,),
        )
        row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Document not found")

    pdf_path = Path(row[0])
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF missing on disk")

    return FileResponse(path=pdf_path, media_type="application/pdf", filename=pdf_path.name)
