from __future__ import annotations

from pathlib import Path

from config import PROCESSED_DIR, RAW_DIR
from bins.s02_processor.smart_extract import smart_extract_pdf


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


def process_single_pdf(pdf_path: Path) -> None:
    """
    Process a single PDF through the smart extraction pipeline and save output.
    """
    result = smart_extract_pdf(pdf_path)

    relative_parent = pdf_path.parent.relative_to(RAW_DIR)
    output_dir = PROCESSED_DIR / relative_parent
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{pdf_path.stem}.txt"
    output_path.write_text(result.clean_text, encoding="utf-8")

    print(f"[PROCESS] {pdf_path.name}")
    print(f"          method={result.method}")
    print(f"          raw_len={result.raw_text_length}")
    print(f"          clean_len={result.clean_text_length}")
    print(f"          saved={output_path}")


def run() -> None:
    """
    Run Phase 2 processing over all PDFs in the raw corpus.
    """
    all_pdf_files = sorted(RAW_DIR.rglob("*.pdf"))

    if not all_pdf_files:
        print("[PROCESS] No PDF files found.")
        return

    # --- FILTER: enforce temporal validity ---
    pdf_files: list[Path] = []
    skipped: list[Path] = []

    for p in all_pdf_files:
        year = _safe_infer_year(p)
        if year == -1:
            skipped.append(p)
        else:
            pdf_files.append(p)

    if skipped:
        print(f"[PROCESS] Skipping {len(skipped)} non-temporal files:")
        for s in skipped:
            print(f"  - {s}")

    # --- PROCESS ONLY VALID FILES ---
    for pdf_path in pdf_files:
        process_single_pdf(pdf_path)


if __name__ == "__main__":
    run()