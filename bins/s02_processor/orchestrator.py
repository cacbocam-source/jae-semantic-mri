from __future__ import annotations

from pathlib import Path

from config import PROCESSED_DIR, RAW_DIR
from bins.s02_processor.smart_extract import smart_extract_pdf


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
    pdf_files = sorted(RAW_DIR.rglob("*.pdf"))

    if not pdf_files:
        print("[PROCESS] No PDF files found.")
        return

    for pdf_path in pdf_files:
        process_single_pdf(pdf_path)


if __name__ == "__main__":
    run()