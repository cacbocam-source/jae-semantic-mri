from __future__ import annotations

from pathlib import Path

from config import MASTER_LEDGER, PROCESSED_DIR, RAW_DIR
from bins.s01_ingest.ledger import rebuild_ledger_from_raw_corpus


def scan_raw_pdfs() -> list[Path]:
    """
    Return all PDFs under the raw corpus directory.
    """
    return sorted(RAW_DIR.rglob("*.pdf"))


def scan_processed_texts() -> list[Path]:
    """
    Return all processed text files under the processed corpus directory.
    """
    return sorted(PROCESSED_DIR.rglob("*.txt"))


def run() -> None:
    """
    Build or update the master ledger from the current corpus state.
    """
    raw_pdfs = scan_raw_pdfs()
    processed_texts = scan_processed_texts()

    print("[INGEST] Corpus scan starting...")
    print(f"         raw_pdfs={len(raw_pdfs)}")
    print(f"         processed_texts={len(processed_texts)}")

    ledger_path = rebuild_ledger_from_raw_corpus()

    print("[INGEST] Ledger update complete.")
    print(f"         ledger={ledger_path}")
    print(f"         exists={ledger_path.exists()}")
    print(f"         output={MASTER_LEDGER}")


if __name__ == "__main__":
    run()