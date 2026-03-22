from __future__ import annotations

from pathlib import Path
import numpy as np

from config import STRUCTURED_DIR, EMBEDDINGS_DIR
from bins.s01_ingest.ledger import make_doc_id


def generate_embedding(text: str) -> np.ndarray:
    """
    Placeholder embedding generator.

    Replace with actual embedding model.
    Must return a fixed-size numeric vector.
    """
    return np.random.rand(768).astype(np.float32)


def embed_single_file(json_path: Path, pdf_path: Path) -> None:
    """
    Generate and persist embedding for a single structured JSON file.

    Parameters:
    - json_path: path to structured JSON (content source)
    - pdf_path: original PDF path (identity source for doc_id)

    Invariants:
    - json_path MUST reside under STRUCTURED_DIR
    - output mirrors STRUCTURED_DIR hierarchy inside EMBEDDINGS_DIR
    """

    # --- VALIDATION: enforce correct pipeline stage (STRUCTURED) ---
    try:
        relative_parent = json_path.parent.relative_to(STRUCTURED_DIR)
    except ValueError as exc:
        raise RuntimeError(
            f"[EMBED] Invalid path: {json_path} is not under STRUCTURED_DIR"
        ) from exc

    # --- LOAD CONTENT ---
    try:
        text = json_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"[EMBED] Failed to read {json_path}: {exc}") from exc

    # --- GENERATE EMBEDDING ---
    embedding = generate_embedding(text)

    # --- VALIDATE EMBEDDING (structural, non-redundant) ---
    if embedding.ndim != 1:
        raise ValueError("[EMBED] Embedding must be a 1D vector")

    if embedding.size == 0:
        raise ValueError("[EMBED] Empty embedding vector")

    if not np.isfinite(embedding).all():
        raise ValueError("[EMBED] Embedding contains NaN or infinite values")

    # --- PREP OUTPUT DIRECTORY ---
    output_dir = EMBEDDINGS_DIR / relative_parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- CREATE STABLE DOC ID (CRITICAL: use PDF path) ---
    try:
        doc_id = make_doc_id(pdf_path)
    except Exception as exc:
        raise RuntimeError(f"[EMBED] Failed to generate doc_id for {pdf_path}: {exc}") from exc

    # --- UNIQUE OUTPUT FILE (no overwrite) ---
    output_path = output_dir / f"{doc_id}.npz"

    # --- SAVE ---
    try:
        np.savez(
            output_path,
            embedding=embedding,
            source=str(json_path),
            doc_id=doc_id,
        )
    except Exception as exc:
        raise RuntimeError(f"[EMBED] Failed to save {output_path}: {exc}") from exc

    # --- LOG ---
    print(f"[EMBED] {json_path.name}")
    print(f"        saved={output_path}")


def run() -> None:
    """
    Batch embedding generation across all structured documents.

    NOTE:
    This standalone runner is less preferred because it lacks the original PDF path.
    Use orchestrator for full pipeline correctness.
    """

    json_files = sorted(STRUCTURED_DIR.rglob("*.json"))

    if not json_files:
        print("[EMBED] No structured files found.")
        return

    print(f"[EMBED] Processing {len(json_files)} structured documents...")

    for json_path in json_files:
        # Fallback: attempt to infer PDF path (best-effort)
        try:
            # Replace .json with .pdf and swap base dir (STRUCTURED → RAW)
            pdf_guess = Path(str(json_path).replace("structured", "raw")).with_suffix(".pdf")
            embed_single_file(json_path, pdf_guess)
        except Exception as exc:
            print(f"[EMBED][FAIL] {json_path}: {exc}")


if __name__ == "__main__":
    run()