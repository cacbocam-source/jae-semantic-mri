import re
import unicodedata

from config import STOP_SECTION_PATTERN


def normalize_text(text: str) -> str:
    """
    Normalize extracted PDF/OCR text for downstream processing.

    Steps:
    - Unicode normalization
    - fix line-break hyphenation
    - normalize line endings
    - collapse excessive blank lines
    - trim trailing spaces
    - collapse repeated inline whitespace
    """
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)

    # Fix common PDF/OCR hyphenation across line breaks:
    # e.g., "self-\nconfidence" -> "selfconfidence"
    text = re.sub(r"-\n(?=[a-z])", "", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing spaces on each line
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    # Collapse repeated spaces/tabs inside lines
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def apply_hard_stop(text: str, stop_pattern: str = STOP_SECTION_PATTERN) -> str:
    """
    Remove back matter such as references, acknowledgements, and funding
    from extracted text.
    """
    if not text:
        return ""

    parts = re.split(stop_pattern, text, flags=re.IGNORECASE)
    return parts[0].strip() if parts else text.strip()


def clean_extracted_text(text: str) -> str:
    """
    Full text-cleaning pipeline for extracted PDF text.
    """
    text = normalize_text(text)
    text = apply_hard_stop(text)
    return text.strip()

if __name__ == "__main__":
    print("Cleaning module loaded successfully.")