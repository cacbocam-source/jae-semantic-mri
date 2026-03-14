from __future__ import annotations

from config import RAW_ROUTE_LEGACY, RAW_ROUTE_MODERN
from bins.s02_processor.smart_extract import smart_extract_pdf


def run_extraction_diagnostic() -> None:
    """
    Run benchmark diagnostics against one modern PDF and one legacy scanned PDF.
    """
    tests = [
        {"label": "Modern", "pdf_path": RAW_ROUTE_MODERN / "2026.pdf"},
        {"label": "Legacy", "pdf_path": RAW_ROUTE_LEGACY / "Vol1_1.pdf"},
    ]

    print("=" * 72)
    print("PHASE 2 DIAGNOSTIC: SMART PDF EXTRACTION ENGINE")
    print("=" * 72)

    for test in tests:
        pdf_path = test["pdf_path"]
        label = test["label"]

        print()
        print(f"[*] Testing {label} PDF: {pdf_path.name}")

        if not pdf_path.exists():
            print(f"[!] Missing file: {pdf_path}")
            continue

        result = smart_extract_pdf(pdf_path)

        preview = result.clean_text[:300].replace("\n", " ")

        print(f"    - Method Used      : {result.method}")
        print(f"    - Page Count       : {result.page_count}")
        print(f"    - Extracted Pages  : {result.extracted_pages}")
        print(f"    - Raw Text Length  : {result.raw_text_length}")
        print(f"    - Clean Text Length: {result.clean_text_length}")
        print(f"    - Preview          : {preview}")
        print("-" * 72)


if __name__ == "__main__":
    run_extraction_diagnostic()