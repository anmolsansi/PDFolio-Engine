# PDFolio Engine

Local-only pipeline to convert HTML to PDF, index HTML text with SQLite FTS5, and return complete PDFs for matching queries.

## Why
- Preserve source HTML and generate PDFs via Chromium print.
- Search is fast and local; no LLM or external APIs required.
- Results return the original PDFs without modification.

## Architecture (high level)
```
HTML folder -> Playwright print -> PDF folder
        \-> HTML text -> SQLite FTS5 index -> /search -> /download
```

## Repo layout
```
app/
  main.py
  routes_search.py
  services/
  models/
scripts/
  ingest.py
web/
  index.html
```

## Local-only files (never committed)
Add these to your machine only:
- `local_config.yaml`
- `prompts/`
- `data/`
- `.env`

The repo already ignores them in `.gitignore`.

## Setup
1) Create your local data folder (outside git):
```
~/html_pdf_kb/
  html/
  pdf/
  index/
```
2) Copy config:
```
cp local_config.example.yaml local_config.yaml
```
3) Install dependencies:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m playwright install chromium
```

## Ingest HTML -> PDF + Index
```
python scripts/ingest.py
```
You can override paths:
```
python scripts/ingest.py --html-root /path/to/html --pdf-root /path/to/pdf --db-path /path/to/kb.sqlite
```

## Run API + UI
```
uvicorn app.main:app --reload
```
Open http://localhost:8000

## Docker
```
HOST_DATA_ROOT=~/html_pdf_kb docker compose up --build
```

## Notes
- Printing to PDF is the closest practical method to preserve layout.
- Original HTML remains on disk to guarantee no data loss.
