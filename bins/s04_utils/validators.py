from __future__ import annotations

from typing import Any

from bins.s04_utils.schemas import (
    A_INTRO,
    A_METHODS,
    A_RESULTS,
    SECTION_KEYS,
    SECTION_NOT_FOUND,
)


def normalize_section_text(value: str) -> str:
    text = str(value).strip()
    if not text:
        return SECTION_NOT_FOUND
    return text


def validate_section_mapping(sections: dict[str, str]) -> dict[str, str]:
    missing: list[str] = [key for key in SECTION_KEYS if key not in sections]
    if missing:
        raise ValueError(f"Section mapping missing required keys: {missing}")

    normalized: dict[str, str] = {}
    for key in SECTION_KEYS:
        normalized[key] = normalize_section_text(sections[key])

    return normalized


def validate_structured_payload(payload: dict[str, Any]) -> None:
    required: set[str] = {
        "doc_id",
        "route",
        "year",
        "extraction_method",
        "page_count",
        "raw_text_length",
        "clean_text_length",
        "segmentation_strategy",
        A_INTRO,
        A_METHODS,
        A_RESULTS,
    }

    missing: list[str] = sorted(key for key in required if key not in payload)
    if missing:
        raise ValueError(f"Structured payload missing required keys: {missing}")


def is_real_section_text(value: str) -> bool:
    text = str(value).strip()
    return bool(text and text != SECTION_NOT_FOUND)