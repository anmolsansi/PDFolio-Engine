from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AppConfig:
    data_root: Path
    html_dir: Path
    pdf_dir: Path
    index_dir: Path
    index_db: Path


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config() -> AppConfig:
    config_path = Path(os.getenv("LOCAL_CONFIG", "local_config.yaml"))
    config_data = _load_yaml(config_path)

    data_root = Path(os.getenv("DATA_ROOT", ""))
    if not data_root.as_posix():
        data_root = Path(config_data.get("data_root", "~/html_pdf_kb")).expanduser()

    html_dir = data_root / "html"
    pdf_dir = data_root / "pdf"
    index_dir = data_root / "index"
    index_db = index_dir / "kb.sqlite"

    return AppConfig(
        data_root=data_root,
        html_dir=html_dir,
        pdf_dir=pdf_dir,
        index_dir=index_dir,
        index_db=index_db,
    )
