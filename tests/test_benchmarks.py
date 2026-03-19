from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable when running:
# python tests/test_benchmarks.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import RAW_ROUTE_LEGACY, RAW_ROUTE_MODERN
from bins.s02_processor.segmenter import UniversalSegmenter
from bins.s02_processor.smart_extract import smart_extract_pdf
from bins.s04_utils.schemas import (
    A_INTRO,
    A_METHODS,
    A_RESULTS,
    A_TAK,
    SECTION_KEYS,
    SECTION_NOT_FOUND,
)
from bins.s04_utils.validators import is_real_section_text


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_modern_extraction() -> None:
    pdf_path = RAW_ROUTE_MODERN / "2026.pdf"
    assert_true(pdf_path.exists(), f"Missing benchmark file: {pdf_path}")

    result = smart_extract_pdf(pdf_path)

    assert_true(result.method == "fitz", f"Expected fitz, got {result.method}")
    assert_true(result.page_count > 0, "Modern benchmark page count must be > 0")
    assert_true(result.raw_text_length > 0, "Modern raw text length must be > 0")
    assert_true(result.clean_text_length > 0, "Modern clean text length must be > 0")


def test_legacy_extraction() -> None:
    pdf_path = RAW_ROUTE_LEGACY / "Vol1_1.pdf"
    assert_true(pdf_path.exists(), f"Missing benchmark file: {pdf_path}")

    result = smart_extract_pdf(pdf_path)

    assert_true(result.method == "ocr", f"Expected ocr, got {result.method}")
    assert_true(result.page_count > 0, "Legacy benchmark page count must be > 0")
    assert_true(result.raw_text_length > 0, "Legacy raw text length must be > 0")
    assert_true(result.clean_text_length > 0, "Legacy clean text length must be > 0")


def test_modern_segmentation() -> None:
    pdf_path = RAW_ROUTE_MODERN / "2026.pdf"
    extracted = smart_extract_pdf(pdf_path)
    sections = UniversalSegmenter(extracted.clean_text, 2026).get_sections()

    expected_keys = set(SECTION_KEYS)
    assert_true(set(sections.keys()) == expected_keys, "Modern segmentation keys mismatch")

    for key in SECTION_KEYS:
        assert_true(key in sections, f"Missing modern section key: {key}")
        assert_true(sections[key] != SECTION_NOT_FOUND, f"Modern {key} not found")
        assert_true(is_real_section_text(sections[key]), f"Modern {key} must be real text")


def test_legacy_segmentation() -> None:
    pdf_path = RAW_ROUTE_LEGACY / "Vol1_1.pdf"
    extracted = smart_extract_pdf(pdf_path)
    sections = UniversalSegmenter(extracted.clean_text, 1960).get_sections()

    expected_keys = set(SECTION_KEYS)
    assert_true(set(sections.keys()) == expected_keys, "Legacy segmentation keys mismatch")

    for key in SECTION_KEYS:
        assert_true(key in sections, f"Missing legacy section key: {key}")
        assert_true(sections[key] != SECTION_NOT_FOUND, f"Legacy {key} not found")
        assert_true(is_real_section_text(sections[key]), f"Legacy {key} must be real text")


def test_canonical_segmentation_schema() -> None:
    pdf_path = RAW_ROUTE_MODERN / "2026.pdf"
    extracted = smart_extract_pdf(pdf_path)
    sections = UniversalSegmenter(extracted.clean_text, 2026).get_sections()

    assert_true(A_TAK in sections, "Missing canonical key A_TAK")
    assert_true(A_INTRO in sections, "Missing canonical key A_intro")
    assert_true(A_METHODS in sections, "Missing canonical key A_methods")
    assert_true(A_RESULTS in sections, "Missing canonical key A_results")

    assert_true("A_Intro" not in sections, "Legacy key A_Intro must not appear")
    assert_true("A_Methods" not in sections, "Legacy key A_Methods must not appear")
    assert_true("A_Results" not in sections, "Legacy key A_Results must not appear")


def run_all_tests() -> None:
    tests = [
        ("Modern Extraction", test_modern_extraction),
        ("Legacy Extraction", test_legacy_extraction),
        ("Modern Segmentation", test_modern_segmentation),
        ("Legacy Segmentation", test_legacy_segmentation),
        ("Canonical Segmentation Schema", test_canonical_segmentation_schema),
    ]

    print("=" * 72)
    print("PHASE 2.3 BENCHMARK REGRESSION TESTS")
    print("=" * 72)

    passed = 0

    for label, test_fn in tests:
        try:
            test_fn()
            print(f"[PASS] {label}")
            passed += 1
        except Exception as exc:
            print(f"[FAIL] {label}: {exc}")

    print("-" * 72)
    print(f"Passed {passed}/{len(tests)} tests")

    if passed != len(tests):
        raise SystemExit(1)


if __name__ == "__main__":
    run_all_tests()