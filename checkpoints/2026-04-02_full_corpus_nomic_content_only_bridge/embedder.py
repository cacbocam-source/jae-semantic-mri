from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from config import EMBEDDINGS_DIR, STRUCTURED_DIR
from bins.s01_ingest.ledger import infer_route, make_doc_id
from bins.s04_utils.schemas import (
    EMBEDDING_BUNDLE_KEY_DOC_ID,
    EMBEDDING_BUNDLE_KEY_EMBEDDINGS,
    EMBEDDING_BUNDLE_KEY_ROUTE,
    EMBEDDING_BUNDLE_KEY_SECTION_LABELS,
    EMBEDDING_BUNDLE_KEY_SOURCE_PATH,
)

MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
EMBEDDING_DIM = 768
DOCUMENT_PREFIX = "search_document: "
UNIT_NORM_TOLERANCE = 0.01

RAW_DIR = STRUCTURED_DIR.parent / "raw"

_model: SentenceTransformer | None = None


def _select_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(
            MODEL_NAME,
            trust_remote_code=True,
            device=_select_device(),
        )
    return _model


def generate_embedding(text: str) -> np.ndarray:
    model = _get_model()
    prefixed = f"{DOCUMENT_PREFIX}{text}"

    vector = np.asarray(
        model.encode(  # pyright: ignore[reportUnknownMemberType]
            prefixed,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        ),
        dtype=np.float32,
    )

    if vector.ndim != 1:
        raise ValueError(f"[EMBED] Expected 1D vector, got ndim={vector.ndim}")
    if vector.shape[0] != EMBEDDING_DIM:
        raise ValueError(
            f"[EMBED] Embedding width must be {EMBEDDING_DIM}, got {vector.shape[0]}"
        )
    if not np.isfinite(vector).all():
        raise ValueError("[EMBED] Embedding contains NaN or infinite values")

    norm = float(np.linalg.norm(vector))
    if not (1.0 - UNIT_NORM_TOLERANCE <= norm <= 1.0 + UNIT_NORM_TOLERANCE):
        raise ValueError(
            f"[EMBED] Embedding is not L2-normalised (norm={norm:.6f}). "
            "Check that normalize_embeddings=True is set."
        )

    return vector


def _load_structured_text(json_path: Path) -> str:
    """
    Build a deterministic, content-only document text payload.

    Only semantically meaningful article sections are embedded.
    Metadata fields such as doc_id, route, year, source paths, page counts,
    and extraction bookkeeping are intentionally excluded.

    Current content contract:
    - A_intro
    - A_methods
    - A_results
    """
    try:
        raw_text = json_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"[EMBED] Failed to read {json_path}: {exc}") from exc

    try:
        parsed: Any = json.loads(raw_text)
    except Exception as exc:
        raise RuntimeError(f"[EMBED] Structured JSON parse failed for {json_path}: {exc}") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError(f"[EMBED] Structured payload must be a JSON object: {json_path}")

    ordered_fields = [
        ("Introduction", parsed.get("A_intro", "")),
        ("Methods", parsed.get("A_methods", "")),
        ("Results", parsed.get("A_results", "")),
    ]

    parts: list[str] = []
    for label, value in ordered_fields:
        if isinstance(value, str):
            cleaned = " ".join(value.split()).strip()
            if cleaned:
                parts.append(f"{label}: {cleaned}")

    if not parts:
        raise RuntimeError(
            f"[EMBED] No content-bearing sections found in {json_path}. "
            "Expected one or more of: A_intro, A_methods, A_results"
        )

    return "\\n\\n".join(parts)


def _infer_pdf_path_from_json(json_path: Path) -> Path:
    try:
        relative_path = json_path.relative_to(STRUCTURED_DIR)
    except ValueError as exc:
        raise RuntimeError(
            f"[EMBED] Invalid path: {json_path} is not under STRUCTURED_DIR"
        ) from exc

    return (RAW_DIR / relative_path).with_suffix(".pdf")


def _save_embedding_bundle(
    *,
    output_path: Path,
    doc_id: str,
    route: str,
    section_labels: np.ndarray,
    embeddings: np.ndarray,
    source_path: Path,
) -> None:
    payload: dict[str, np.ndarray] = {
        EMBEDDING_BUNDLE_KEY_DOC_ID: np.asarray(doc_id, dtype=np.str_),
        EMBEDDING_BUNDLE_KEY_ROUTE: np.asarray(route, dtype=np.str_),
        EMBEDDING_BUNDLE_KEY_SECTION_LABELS: np.asarray(section_labels, dtype=np.str_),
        EMBEDDING_BUNDLE_KEY_EMBEDDINGS: np.asarray(embeddings, dtype=np.float32),
        EMBEDDING_BUNDLE_KEY_SOURCE_PATH: np.asarray(str(source_path), dtype=np.str_),
    }

    try:
        np.savez_compressed(output_path, **payload)  # pyright: ignore[reportArgumentType]
    except Exception as exc:
        raise RuntimeError(f"[EMBED] Failed to save {output_path}: {exc}") from exc


def embed_single_file(json_path: Path, pdf_path: Path | None = None) -> None:
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

    route = infer_route(pdf_path).strip()
    if not route:
        raise ValueError(f"[EMBED] Could not infer route from PDF path: {pdf_path}")

    doc_id = make_doc_id(pdf_path)

    section_labels = np.asarray(["document"], dtype=np.str_)
    embeddings = np.asarray([vector], dtype=np.float32)

    output_dir = EMBEDDINGS_DIR / relative_parent
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{doc_id}.npz"

    _save_embedding_bundle(
        output_path=output_path,
        doc_id=doc_id,
        route=route,
        section_labels=section_labels,
        embeddings=embeddings,
        source_path=json_path,
    )

    print(f"[EMBED] {json_path.name}")
    print(f"        saved={output_path}")


def run() -> None:
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
