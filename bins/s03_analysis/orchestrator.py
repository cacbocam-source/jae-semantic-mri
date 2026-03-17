from __future__ import annotations

from config import RAW_DIR
from bins.s01_ingest.ledger import infer_route, make_doc_id
from bins.s03_analysis.section_export import infer_year_from_path, write_section_export
from bins.s04_utils.manifest_manager import (
    mark_stage_failure,
    mark_stage_success,
    seed_manifest_from_raw_pdfs,
)


def run() -> None:
    """
    Export structured section JSON artifacts for all PDFs in the raw corpus.
    """
    pdf_files = sorted(RAW_DIR.rglob("*.pdf"))

    if not pdf_files:
        print("[ANALYSIS] No PDF files found.")
        return

    seed_manifest_from_raw_pdfs(
        pdf_files,
        infer_route=infer_route,
        infer_year=infer_year_from_path,
        make_doc_id=make_doc_id,
    )

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