from __future__ import annotations

from pathlib import Path

from config import RAW_DIR
from bins.s01_ingest.ledger import infer_route, make_doc_id
from bins.s03_analysis.section_export import write_section_export
from bins.s04_utils.manifest_manager import (
    mark_stage_failure,
    mark_stage_success,
    seed_manifest_from_raw_pdfs,
)


def _safe_infer_year(path: Path) -> int:
    """
    Robust year inference supporting:
    1. Folder-based legacy: .../<YEAR>/<file>.pdf
    2. Filename-based modern: .../2026.pdf

    Returns:
        int year OR -1 if not resolvable (e.g., Vol1_1.pdf)
    """

    # Case 1 — folder-based
    for part in path.parts:
        if part.isdigit() and len(part) == 4:
            return int(part)

    # Case 2 — filename-based
    stem = path.stem
    if stem.isdigit() and len(stem) == 4:
        return int(stem)

    # Case 3 — unresolved
    return -1


def run() -> None:
    """
    Export structured section JSON artifacts for all PDFs in the raw corpus.
    """
    all_pdf_files = sorted(RAW_DIR.rglob("*.pdf"))

    if not all_pdf_files:
        print("[ANALYSIS] No PDF files found.")
        return

    # --- FILTER: only include resolvable-year documents ---
    pdf_files: list[Path] = []
    skipped: list[Path] = []

    for p in all_pdf_files:
        year = _safe_infer_year(p)
        if year == -1:
            skipped.append(p)
        else:
            pdf_files.append(p)

    if skipped:
        print(f"[ANALYSIS] Skipping {len(skipped)} non-temporal files:")
        for s in skipped:
            print(f"  - {s}")

    # --- Seed manifest (only valid files) ---
    seed_manifest_from_raw_pdfs(
        pdf_files,
        infer_route=infer_route,
        infer_year=_safe_infer_year,
        make_doc_id=make_doc_id,
    )

    # --- Process valid documents only ---
    for pdf_path in pdf_files:
        doc_id = make_doc_id(pdf_path)
        try:
            output_path = write_section_export(pdf_path)
            mark_stage_success(doc_id, "structured_status")
            print(f"[ANALYSIS] exported={output_path}")
        except Exception as exc:
            mark_stage_failure(doc_id, "structured_status", str(exc))
            print(f"[ANALYSIS][FAIL] {pdf_path}: {exc}")


if __name__ == "__main__":
    run()