from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import load_config
from app.services.indexer import ingest_html_folder


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest HTML files into PDF + FTS index")
    parser.add_argument("--html-root", type=str, help="Override HTML root folder")
    parser.add_argument("--pdf-root", type=str, help="Override PDF output folder")
    parser.add_argument("--db-path", type=str, help="Override SQLite db path")
    args = parser.parse_args()

    config = load_config()
    html_root = Path(args.html_root) if args.html_root else config.html_dir
    pdf_root = Path(args.pdf_root) if args.pdf_root else config.pdf_dir
    db_path = Path(args.db_path) if args.db_path else config.index_db

    if not html_root.exists():
        raise SystemExit(f"HTML root not found: {html_root}")

    stats = ingest_html_folder(html_root, pdf_root, db_path)
    print(
        "Ingest complete: "
        f"processed={stats.processed} updated={stats.updated} "
        f"skipped={stats.skipped} removed={stats.removed}"
    )


if __name__ == "__main__":
    main()
