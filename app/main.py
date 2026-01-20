from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.routes_search import router as search_router

app = FastAPI(title="PDFolio Engine")
app.include_router(search_router)


@app.get("/")
def index():
    web_index = Path(__file__).resolve().parent.parent / "web" / "index.html"
    return FileResponse(web_index)
