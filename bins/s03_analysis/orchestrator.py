from __future__ import annotations

from pathlib import Path

from config import RAW_DIR
from bins.s01_ingest.ledger import infer_route, make_doc_id
from bins.s03_analysis.section_export import write_section_export
from bins.s03_analysis.embedder import embed_single_file
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
        int year OR -1 if not resolvable
    """
    for part in path.parts:
        if part.isdigit() and len(part) == 4:
            return int(part)

    stem = path.stem
    if stem.isdigit() and len(stem) == 4:
        return int(stem)

    return -1


def _filter_valid_pdfs(pdf_paths: list[Path]) -> tuple[list[Path], list[Path]]:
    """
    Separate valid and non-temporal PDFs.
    """
    valid: list[Path] = []
    skipped: list[Path] = []

    for p in pdf_paths:
        year = _safe_infer_year(p)
        if year == -1:
            skipped.append(p)
        else:
            valid.append(p)

    return valid, skipped


def run() -> None:
    """
    Phase 3 pipeline:
    structured export → embeddings → (metrics downstream)
    """

    all_pdf_files = sorted(RAW_DIR.rglob("*.pdf"))

    if not all_pdf_files:
        print("[ANALYSIS] No PDF files found.")
        return

    # --- FILTER ---
    pdf_files, skipped = _filter_valid_pdfs(all_pdf_files)

    if skipped:
        print(f"[ANALYSIS] Skipping {len(skipped)} non-temporal files:")
        for s in skipped:
            print(f"  - {s}")

    # --- SEED MANIFEST ---
    seed_manifest_from_raw_pdfs(
        pdf_files,
        infer_route=infer_route,
        infer_year=_safe_infer_year,
        make_doc_id=make_doc_id,
    )

    # --- PROCESS PIPELINE ---
    for pdf_path in pdf_files:
        doc_id = make_doc_id(pdf_path)

        try:
            # --- 1. STRUCTURED EXPORT ---
            output_path = write_section_export(pdf_path)
            print(f"[ANALYSIS] exported={output_path}")

            # --- 2. EMBEDDING (FIXED: pass original pdf_path) ---
            embed_single_file(
                json_path=output_path,
                pdf_path=pdf_path,  # 🔴 CRITICAL FIX
            )

            # --- 3. SUCCESS ---
            mark_stage_success(doc_id, "structured_status")

        except Exception as exc:
            mark_stage_failure(doc_id, "structured_status", str(exc))
            print(f"[ANALYSIS][FAIL] {pdf_path}: {exc}")


if __name__ == "__main__":
    run()