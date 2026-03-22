from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from config import STRUCTURED_DIR, EMBEDDINGS_DIR
from bins.s01_ingest.ledger import make_doc_id, infer_route
from bins.s04_utils.schemas import (
    EMBEDDING_BUNDLE_KEY_DOC_ID,
    EMBEDDING_BUNDLE_KEY_EMBEDDINGS,
    EMBEDDING_BUNDLE_KEY_ROUTE,
    EMBEDDING_BUNDLE_KEY_SECTION_LABELS,
    EMBEDDING_BUNDLE_KEY_SOURCE_PATH,
)


EMBEDDING_DIM = 768


def generate_embedding(text: str) -> np.ndarray:
    """
    Placeholder embedding generator.

    Replace with actual embedding model.
    Must return a fixed-size 1D float32 vector of length 768.
    """
    return np.random.rand(EMBEDDING_DIM).astype(np.float32)


def _load_structured_text(json_path: Path) -> str:
    """
    Best-effort structured text loader.

    Current strategy:
    - If JSON parses to a dict/list, serialize it deterministically.
    - Fallback to raw file text.
    """
    try:
        raw_text = json_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"[EMBED] Failed to read {json_path}: {exc}") from exc

    try:
        parsed: Any = json.loads(raw_text)
        return json.dumps(parsed, ensure_ascii=False, sort_keys=True)
    except Exception:
        return raw_text


def _infer_pdf_path_from_json(json_path: Path) -> Path:
    """
    Map structured JSON path back to original PDF path.

    Example:
    data/structured/Route_B_Legacy/1960/foo.json
    -> data/raw/Route_B_Legacy/1960/foo.pdf
    """
    try:
        relative_path = json_path.relative_to(STRUCTURED_DIR)
    except ValueError as exc:
        raise RuntimeError(
            f"[EMBED] Invalid path: {json_path} is not under STRUCTURED_DIR"
        ) from exc

    pdf_path = Path("data/raw") / relative_path
    return pdf_path.with_suffix(".pdf")


def embed_single_file(json_path: Path, pdf_path: Path | None = None) -> None:
    """
    Generate and persist a schema-compliant embedding bundle for one structured JSON file.

    Bundle schema:
    - doc_id: scalar
    - route: scalar
    - section_labels: 1D object array
    - embeddings: 2D float32 array, shape (n_sections, 768)
    - source_path: scalar
    """
    try:
        relative_parent = json_path.parent.relative_to(STRUCTURED_DIR)
    except ValueError as exc:
        raise RuntimeError(
            f"[EMBED] Invalid path: {json_path} is not under STRUCTURED_DIR"
        ) from exc

    if pdf_path is None:
        pdf_path = _infer_pdf_path_from_json(json_path)

    text = _load_structured_text(json_path)
    vector = generate_embedding(text)

    if vector.ndim != 1:
        raise ValueError("[EMBED] Embedding must be a 1D vector")
    if vector.shape[0] != EMBEDDING_DIM:
        raise ValueError(
            f"[EMBED] Embedding width must be {EMBEDDING_DIM}, got {vector.shape[0]}"
        )
    if not np.isfinite(vector).all():
        raise ValueError("[EMBED] Embedding contains NaN or infinite values")

    route = infer_route(pdf_path).strip()
    if not route:
        raise ValueError(f"[EMBED] Could not infer route from PDF path: {pdf_path}")

    doc_id = make_doc_id(pdf_path)

    # Current corpus implementation uses one embedding per document.
    section_labels = np.asarray(["document"], dtype=object)
    embeddings = np.asarray([vector], dtype=np.float32)

    output_dir = EMBEDDINGS_DIR / relative_parent
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{doc_id}.npz"

    try:
        np.savez(
            output_path,
            **{
                EMBEDDING_BUNDLE_KEY_DOC_ID: np.asarray(doc_id),
                EMBEDDING_BUNDLE_KEY_ROUTE: np.asarray(route),
                EMBEDDING_BUNDLE_KEY_SECTION_LABELS: section_labels,
                EMBEDDING_BUNDLE_KEY_EMBEDDINGS: embeddings,
                EMBEDDING_BUNDLE_KEY_SOURCE_PATH: np.asarray(str(json_path)),
            },
        )
    except Exception as exc:
        raise RuntimeError(f"[EMBED] Failed to save {output_path}: {exc}") from exc

    print(f"[EMBED] {json_path.name}")
    print(f"        saved={output_path}")


def run() -> None:
    """
    Batch embedding generation across all structured documents.
    """
    json_files = sorted(STRUCTURED_DIR.rglob("*.json"))

    if not json_files:
        print("[EMBED] No structured files found.")
        return

    print(f"[EMBED] Processing {len(json_files)} structured documents...")

    for json_path in json_files:
        try:
            pdf_path = _infer_pdf_path_from_json(json_path)
            embed_single_file(json_path=json_path, pdf_path=pdf_path)
        except Exception as exc:
            print(f"[EMBED][FAIL] {json_path}: {exc}")


if __name__ == "__main__":
    run()