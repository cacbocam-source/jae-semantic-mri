from __future__ import annotations

from config import RAW_DIR
from bins.s03_analysis.section_export import write_section_export


def run() -> None:
    """
    Export structured section JSON artifacts for all PDFs in the raw corpus.
    """
    pdf_files = sorted(RAW_DIR.rglob("*.pdf"))

    if not pdf_files:
        print("[ANALYSIS] No PDF files found.")
        return

    for pdf_path in pdf_files:
        output_path = write_section_export(pdf_path)
        print(f"[ANALYSIS] exported={output_path}")


if __name__ == "__main__":
    run()