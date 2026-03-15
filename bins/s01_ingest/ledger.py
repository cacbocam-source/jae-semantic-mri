from __future__ import annotations

import csv
import hashlib
from datetime import datetime, UTC
from pathlib import Path

from config import MASTER_LEDGER, PROCESSED_DIR, RAW_DIR
from bins.s02_processor.smart_extract import smart_extract_pdf


LEDGER_FIELDS = [
    "doc_id",
    "source_filename",
    "source_pdf_path",
    "route",
    "processed_text_path",
    "extraction_method",
    "page_count",
    "raw_text_length",
    "clean_text_length",
    "status",
    "processed_timestamp",
]


def init_ledger() -> None:
    """
    Create the master ledger if it does not already exist.
    """
    MASTER_LEDGER.parent.mkdir(parents=True, exist_ok=True)

    if MASTER_LEDGER.exists():
        return

    with MASTER_LEDGER.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        writer.writeheader()


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


def infer_processed_text_path(pdf_path: Path) -> Path:
    """
    Map a raw PDF path to its expected processed text path.
    """
    relative_path = pdf_path.relative_to(RAW_DIR)
    return (PROCESSED_DIR / relative_path).with_suffix(".txt")


def build_record(pdf_path: Path) -> dict[str, str]:
    """
    Build a ledger record from a raw PDF by invoking the smart extraction pipeline.

    Note:
    This recomputes extraction metadata to ensure the ledger contains method,
    page count, and text lengths. This is acceptable for the current baseline
    build and can be optimized later by persisting processor metadata directly.
    """
    result = smart_extract_pdf(pdf_path)
    processed_text_path = infer_processed_text_path(pdf_path)

    status = "processed" if processed_text_path.exists() else "processed_text_missing"

    clean_text_length = result.clean_text_length
    if processed_text_path.exists():
        clean_text_length = len(processed_text_path.read_text(encoding="utf-8"))

    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat()

    return {
        "doc_id": make_doc_id(pdf_path),
        "source_filename": pdf_path.name,
        "source_pdf_path": str(pdf_path.resolve()),
        "route": infer_route(pdf_path),
        "processed_text_path": str(processed_text_path.resolve()),
        "extraction_method": result.method,
        "page_count": str(result.page_count),
        "raw_text_length": str(result.raw_text_length),
        "clean_text_length": str(clean_text_length),
        "status": status,
        "processed_timestamp": timestamp,
    }


def load_existing_rows() -> dict[str, dict[str, str]]:
    """
    Load existing ledger rows keyed by doc_id.
    """
    if not MASTER_LEDGER.exists():
        return {}

    with MASTER_LEDGER.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["doc_id"]: row for row in reader}


def write_rows(rows: list[dict[str, str]]) -> None:
    """
    Rewrite the ledger with the provided rows.
    """
    with MASTER_LEDGER.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def rebuild_ledger_from_raw_corpus() -> Path:
    """
    Rebuild or update the ledger from all PDFs under data/raw/.
    """
    init_ledger()
    existing = load_existing_rows()

    pdf_files = sorted(RAW_DIR.rglob("*.pdf"))

    for pdf_path in pdf_files:
        record = build_record(pdf_path)
        existing[record["doc_id"]] = record

    rows = sorted(existing.values(), key=lambda row: row["source_pdf_path"])
    write_rows(rows)

    return MASTER_LEDGER