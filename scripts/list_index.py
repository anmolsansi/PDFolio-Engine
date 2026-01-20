from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlite3 import connect

from app.config import load_config


def main() -> None:
    config = load_config()
    db_path = config.index_db
    if not db_path.exists():
        raise SystemExit(f"Index not found: {db_path}")

    with connect(db_path) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM documents")
        total = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM documents_fts")
        fts_total = cur.fetchone()[0]

    print(f"documents={total} fts_rows={fts_total} db={db_path}")


if __name__ == "__main__":
    main()
