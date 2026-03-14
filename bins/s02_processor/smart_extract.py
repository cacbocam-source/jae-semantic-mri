from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import MIN_DIGITAL_TEXT_LENGTH
from bins.s02_processor.cleaning import clean_extracted_text
from bins.s02_processor.digital_extract import extract_text_with_fitz_diagnostics
from bins.s02_processor.ocr_engine import perform_ocr_diagnostics


@dataclass(frozen=True)
class SmartExtractionResult:
    """
    Structured result for the smart PDF extraction pipeline.

    Attributes
    ----------
    pdf_path : str
        Absolute path to the source PDF.
    method : str
        Extraction method used: 'fitz' or 'ocr'.
    page_count : int
        Number of pages in the document.
    extracted_pages : int
        Number of pages successfully processed.
    raw_text_length : int
        Character length before cleaning.
    clean_text_length : int
        Character length after cleaning.
    clean_text : str
        Final cleaned text ready for downstream processing.
    """
    pdf_path: str
    method: str
    page_count: int
    extracted_pages: int
    raw_text_length: int
    clean_text_length: int
    clean_text: str


def smart_extract_pdf(pdf_path: str | Path) -> SmartExtractionResult:
    """
    Smart extraction gateway for PDFs.

    Workflow
    --------
    1. Attempt fast digital extraction using PyMuPDF.
    2. If extracted text meets threshold, use it.
    3. Otherwise, fall back to OCR.
    4. Clean the extracted text for downstream use.

    Parameters
    ----------
    pdf_path : str | Path
        Path to the PDF file.

    Returns
    -------
    SmartExtractionResult
        Structured extraction result.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    RuntimeError
        If neither extraction path succeeds.
    """
    path = Path(pdf_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    # Phase 1: Attempt digital extraction
    digital_result = extract_text_with_fitz_diagnostics(path)

    if digital_result.raw_text_length >= MIN_DIGITAL_TEXT_LENGTH:
        clean_text = clean_extracted_text(digital_result.raw_text)

        return SmartExtractionResult(
            pdf_path=digital_result.pdf_path,
            method="fitz",
            page_count=digital_result.page_count,
            extracted_pages=digital_result.extracted_pages,
            raw_text_length=digital_result.raw_text_length,
            clean_text_length=len(clean_text),
            clean_text=clean_text,
        )

    # Phase 2: Fall back to OCR
    ocr_result = perform_ocr_diagnostics(path)
    clean_text = clean_extracted_text(ocr_result.raw_text)

    return SmartExtractionResult(
        pdf_path=ocr_result.pdf_path,
        method="ocr",
        page_count=ocr_result.page_count,
        extracted_pages=ocr_result.extracted_pages,
        raw_text_length=ocr_result.raw_text_length,
        clean_text_length=len(clean_text),
        clean_text=clean_text,
    )


if __name__ == "__main__":
    print("smart_extract.py is a library module. Import it from the project root.")