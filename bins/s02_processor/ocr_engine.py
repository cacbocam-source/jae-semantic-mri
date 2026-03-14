from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path

from config import OCR_DPI, TESSERACT_LANG


@dataclass(frozen=True)
class OCRExtractionResult:
    """
    Structured result for OCR-based PDF text extraction.

    Attributes
    ----------
    pdf_path : str
        Absolute path to the source PDF.
    page_count : int
        Number of rendered pages.
    extracted_pages : int
        Number of pages successfully OCR-processed.
    raw_text : str
        Concatenated OCR text from all pages.
    raw_text_length : int
        Character length of OCR text.
    """
    pdf_path: str
    page_count: int
    extracted_pages: int
    raw_text: str
    raw_text_length: int


def check_tesseract_available() -> bool:
    """
    Return True if the Tesseract binary is available on PATH.
    """
    return shutil.which("tesseract") is not None


def check_poppler_available() -> bool:
    """
    Return True if the Poppler pdftoppm tool is available on PATH.
    """
    return shutil.which("pdftoppm") is not None


def perform_ocr(pdf_path: str | Path, dpi: int = OCR_DPI, lang: str = TESSERACT_LANG) -> str:
    """
    OCR fallback for scanned PDFs.

    Parameters
    ----------
    pdf_path : str | Path
        Path to the PDF file.
    dpi : int
        Render DPI for PDF-to-image conversion.
    lang : str
        OCR language passed to Tesseract.

    Returns
    -------
    str
        Concatenated OCR text.

    Raises
    ------
    FileNotFoundError
        If the PDF file does not exist.
    EnvironmentError
        If required OCR dependencies are missing.
    RuntimeError
        If conversion or OCR fails.
    """
    result = perform_ocr_diagnostics(pdf_path, dpi=dpi, lang=lang)
    return result.raw_text


def perform_ocr_diagnostics(
    pdf_path: str | Path,
    dpi: int = OCR_DPI,
    lang: str = TESSERACT_LANG,
) -> OCRExtractionResult:
    """
    OCR a PDF and return structured diagnostics.

    Parameters
    ----------
    pdf_path : str | Path
        Path to the PDF file.
    dpi : int
        Render DPI for PDF-to-image conversion.
    lang : str
        OCR language passed to Tesseract.

    Returns
    -------
    OCRExtractionResult
        Structured OCR result with metadata.

    Raises
    ------
    FileNotFoundError
        If the PDF path does not exist.
    EnvironmentError
        If Tesseract or Poppler is unavailable.
    RuntimeError
        If PDF rendering or OCR processing fails.
    """
    path = Path(pdf_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise RuntimeError(f"Expected a PDF file, got: {path}")

    if not check_tesseract_available():
        raise EnvironmentError("Tesseract is not installed or not available on PATH.")

    if not check_poppler_available():
        raise EnvironmentError("Poppler is not installed or pdftoppm is not available on PATH.")

    try:
        images = convert_from_path(str(path), dpi=dpi)
    except Exception as exc:
        raise RuntimeError(f"Failed converting PDF to images: {path}") from exc

    page_count = len(images)
    extracted_pages = 0
    text_parts: list[str] = []

    for page_index, image in enumerate(images, start=1):
        try:
            print(f"    - OCR Page {page_index}/{page_count}")
            page_text = pytesseract.image_to_string(image, lang=lang)
            text_parts.append(page_text)
            extracted_pages += 1
        except Exception as exc:
            raise RuntimeError(
                f"Failed OCR on page {page_index} for {path}"
            ) from exc

    raw_text = "\n".join(text_parts).strip()

    return OCRExtractionResult(
        pdf_path=str(path),
        page_count=page_count,
        extracted_pages=extracted_pages,
        raw_text=raw_text,
        raw_text_length=len(raw_text),
    )


if __name__ == "__main__":
    print("ocr_engine.py is a library module. Import it from the project root.")