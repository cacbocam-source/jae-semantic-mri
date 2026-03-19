from __future__ import annotations

import hashlib
from pathlib import Path

from config import RAW_DIR


def make_doc_id(pdf_path: Path) -> str:
    """
    Create a stable document ID from the raw PDF relative path.
    """
    relative_path = str(pdf_path.relative_to(RAW_DIR))
    digest = hashlib.sha1(relative_path.encode("utf-8")).hexdigest()[:12]
    return f"jae_{digest}"


def infer_route(pdf_path: Path) -> str:
    """
    Infer route from the raw PDF path.
    """
    relative_path = pdf_path.relative_to(RAW_DIR)
    return relative_path.parts[0] if relative_path.parts else "UNKNOWN"


__all__ = [
    "make_doc_id",
    "infer_route",
]