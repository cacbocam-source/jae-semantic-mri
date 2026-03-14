from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass(frozen=True)
class DigitalExtractionResult:
    """
    Structured result for digital PDF text extraction.

    Attributes
    ----------
    pdf_path : str
        Absolute path to the source PDF.
    page_count : int
        Number of pages in the document.
    extracted_pages : int
        Number of pages successfully processed.
    raw_text : str
        Concatenated extracted text from all pages.
    raw_text_length : int
        Character length of extracted text.
    """
    pdf_path: str
    page_count: int
    extracted_pages: int
    raw_text: str
    raw_text_length: int


def extract_text_with_fitz(pdf_path: str | Path) -> str:
    """
    Fast-path text extraction for digital PDFs using PyMuPDF.

    Parameters
    ----------
    pdf_path : str | Path
        Path to the PDF file.

    Returns
    -------
    str
        Concatenated text extracted from the PDF.

    Raises
    ------
    FileNotFoundError
        If the PDF path does not exist.
    RuntimeError
        If the PDF cannot be opened or processed.
    """
    result = extract_text_with_fitz_diagnostics(pdf_path)
    return result.raw_text


def extract_text_with_fitz_diagnostics(pdf_path: str | Path) -> DigitalExtractionResult:
    """
    Extract text from a PDF and return structured diagnostics.

    This is the preferred internal function for the processor layer because it
    preserves useful metadata for logging and validation.

    Parameters
    ----------
    pdf_path : str | Path
        Path to the PDF file.

    Returns
    -------
    DigitalExtractionResult
        Structured extraction result.

    Raises
    ------
    FileNotFoundError
        If the PDF path does not exist.
    RuntimeError
        If the PDF cannot be opened or processed.
    """
    path = Path(pdf_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise RuntimeError(f"Expected a PDF file, got: {path}")

    text_parts: list[str] = []
    extracted_pages = 0

    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise RuntimeError(f"Failed to open PDF with PyMuPDF: {path}") from exc

    try:
        page_count = len(doc)

        for page_index, page in enumerate(doc):
            try:
                page_text = page.get_text("text") or ""
                text_parts.append(page_text)
                extracted_pages += 1
            except Exception as exc:
                raise RuntimeError(
                    f"Failed extracting text from page {page_index} in {path}"
                ) from exc

    finally:
        doc.close()

    raw_text = "\n".join(text_parts).strip()

    return DigitalExtractionResult(
        pdf_path=str(path),
        page_count=page_count,
        extracted_pages=extracted_pages,
        raw_text=raw_text,
        raw_text_length=len(raw_text),
    )


if __name__ == "__main__":
    print("digital_extract.py is a library module. Import it from the project root.")