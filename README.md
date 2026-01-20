# PDFolio Engine

PDFolio Engine is a local-only pipeline that converts HTML to PDF using a real browser engine, builds a fast SQLite FTS5 search index over the HTML text, and returns complete PDF files for matching queries. It is designed for privacy-first knowledge bases and offline document retrieval.

## Highlights
- True local-only operation; no LLMs, no paid APIs, no network required after setup.
- Chromium-based printing via Playwright for faithful HTML → PDF rendering.
- SQLite FTS5 indexing for reliable keyword, phrase, and prefix search.
- Results return the original generated PDFs without modification.
- GitHub-safe repo with local-only config, prompts, and data excluded.

## Architecture (high level)
```
HTML folder -> Playwright print -> PDF folder
        \-> HTML text -> SQLite FTS5 index -> /search -> /download
```

## Use cases
- Personal research vaults (papers, newsletters, saved web pages).
- Internal knowledge bases (documentation snapshots, SOPs).
- Resume-grade pipeline for document ingestion and retrieval.

## Requirements
- Python 3.11+
- Playwright + Chromium runtime
- SQLite (bundled with Python)

## Quickstart
1) Create local data directories:
```
~/html_pdf_kb/
  html/
  pdf/
  index/
```
2) Copy local config:
```
cp local_config.example.yaml local_config.yaml
```
3) Install dependencies:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m playwright install chromium
```
4) Ingest HTML → PDF + Index:
```
python scripts/ingest.py
```
5) Run API + UI:
```
uvicorn app.main:app --reload
```
Open http://localhost:8000

## Local-only data and privacy
The following are intentionally local-only and never committed:
- `local_config.yaml`
- `prompts/`
- `data/`
- `.env`
- `HTML Files/` (if you keep raw HTML inside this repo)

All are already listed in `.gitignore`.

## Data layout (default)
```
~/html_pdf_kb/
  html/                      # source HTML files
  pdf/                       # generated PDFs
  index/
    kb.sqlite                # SQLite DB with FTS index
```

## Configuration
`local_config.yaml` points to the local data root:
```
data_root: "~/html_pdf_kb"
```
You can also override paths via environment:
- `DATA_ROOT=/path/to/root`
- `LOCAL_CONFIG=/path/to/local_config.yaml`

## Ingestion pipeline
Ingestion is deterministic and incremental:
1) Compute SHA-256 for each HTML file.
2) Skip unchanged files (fast re-ingest).
3) Print HTML to PDF via Playwright.
4) Extract visible text with BeautifulSoup.
5) Store metadata and text in SQLite + FTS5.

Run:
```
python scripts/ingest.py
```
Overrides:
```
python scripts/ingest.py --html-root /path/to/html --pdf-root /path/to/pdf --db-path /path/to/kb.sqlite
```

## Search API
```
GET /search?q=your+query&limit=20&offset=0
```
Response:
```
{
  "query": "your query",
  "results": [
    {
      "doc_id": 1,
      "html_path": "/path/to/source.html",
      "pdf_path": "/path/to/output.pdf",
      "score": -3.21,
      "snippet": "..."
    }
  ]
}
```

## Download API
```
GET /download?doc_id=123
```
Returns the original PDF bytes stored on disk, unchanged.

## Query behavior
SQLite FTS5 uses AND semantics by default:
- `chat gpt prompts` means all three tokens must be present.
- Quote phrases: `"emulsifying capacity"`.
- Prefix search is supported with `*`: `emulsan*`.

## Minimal UI
The UI is a single HTML page served at `/`:
- Search input
- Results with snippet and score
- Download link for each PDF

File: `web/index.html`

## Repo layout
```
app/
  main.py                 # FastAPI entrypoint
  routes_search.py        # /search and /download
  services/
    converter.py          # HTML -> PDF via Playwright
    extractor.py          # HTML text extraction
    indexer.py            # SQLite + FTS5 build/update
    searcher.py           # query logic
  models/
    schema.py             # Pydantic models
scripts/
  ingest.py               # batch convert + index
  list_index.py           # index counts
web/
  index.html              # minimal UI
tests/
  test_extractor.py
  test_search.py
```

## Docker
```
HOST_DATA_ROOT=~/html_pdf_kb docker compose up --build
```
This mounts your local data folder into the container at `/data`.

## CI
GitHub Actions runs:
- `ruff` lint
- `pytest` tests

Workflow: `.github/workflows/ci.yml`

## Troubleshooting
- `ModuleNotFoundError: app`:
  Use `python scripts/ingest.py` from repo root. The script sets sys.path.
- Search returns fewer results than expected:
  FTS5 uses AND by default. Try fewer tokens or prefix search.
- HTML uses external assets:
  Local rendering may differ if remote assets are blocked. Consider downloading assets locally.

## Non-negotiables and limitations
- Printing to PDF is the closest practical method to preserve layout.
- Complex or JS-heavy HTML may render differently without live network access.
- Original HTML is always retained, ensuring no loss of source data.

## Roadmap
- Optional semantic recall (local embeddings + FAISS).
- Synonym expansion rules for more forgiving queries.
- UI improvements: pagination, highlight previews, and filters.

## License
MIT (add a LICENSE file if desired).
