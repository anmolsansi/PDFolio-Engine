from __future__ import annotations

from pydantic import BaseModel


class SearchResult(BaseModel):
    doc_id: int
    html_path: str
    pdf_path: str
    score: float
    snippet: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
