from __future__ import annotations

from pathlib import Path
import numpy as np

from config import STRUCTURED_DIR, EMBEDDINGS_DIR
from bins.s01_ingest.ledger import make_doc_id


def generate_embedding(text: str) -> np.ndarray:
    """
    Placeholder embedding generator.
    Replace with your actual embedding model call.
    """
    # Example: simple deterministic vector (replace in production)
    return np.random.rand(768).astype(np.float32)


def embed_single_file(json_path: Path) -> None:
    """
    Generate embeddings for a single structured JSON file.
    """

    # Load structured content
    text = json_path.read_text(encoding="utf-8")

    # Generate embedding
    embedding = generate_embedding(text)

    # Determine route (preserve structure)
    relative_parent = json_path.parent.relative_to(STRUCTURED_DIR)
    output_dir = EMBEDDINGS_DIR / relative_parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create doc_id (CRITICAL FIX)
    doc_id = make_doc_id(json_path)

    # ✅ FIX: unique output per document
    output_path = output_dir / f"{doc_id}.npz"

    # Save embedding
    np.savez(
        output_path,
        embedding=embedding,
        source=str(json_path),
        doc_id=doc_id,
    )

    print(f"[EMBED] {json_path.name}")
    print(f"        saved={output_path}")


def run() -> None:
    """
    Generate embeddings for all structured documents.
    """

    json_files = sorted(STRUCTURED_DIR.rglob("*.json"))

    if not json_files:
        print("[EMBED] No structured files found.")
        return

    for json_path in json_files:
        embed_single_file(json_path)


if __name__ == "__main__":
    run()