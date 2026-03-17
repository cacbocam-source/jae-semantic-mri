from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from bins.s03_analysis.section_export import build_section_export, write_section_export
from bins.s04_utils.schemas import A_INTRO, A_METHODS, A_RESULTS, A_TAK


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_structured_export(path_str: str) -> None:
    output_path = write_section_export(Path(path_str))
    assert_true(output_path.exists(), f"Structured output missing: {output_path}")

    with output_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    required_top_keys = {
        "doc_id",
        "source_filename",
        "source_pdf_path",
        "route",
        "year",
        "extraction_method",
        "page_count",
        "raw_text_length",
        "clean_text_length",
        "segmentation_strategy",
        "A_intro",
        "A_methods",
        "A_results",
    }

    assert_true(
        set(data.keys()) == required_top_keys,
        f"Structured JSON top-level keys mismatch: {set(data.keys())}",
    )

    assert_true("sections" not in data, "Structured JSON must not contain nested 'sections'")
    assert_true("A_Intro" not in data, "Structured JSON must not contain legacy key 'A_Intro'")
    assert_true("A_Methods" not in data, "Structured JSON must not contain legacy key 'A_Methods'")
    assert_true("A_Results" not in data, "Structured JSON must not contain legacy key 'A_Results'")

    assert_true(isinstance(data["A_intro"], str), "A_intro must be a string")
    assert_true(isinstance(data["A_methods"], str), "A_methods must be a string")
    assert_true(isinstance(data["A_results"], str), "A_results must be a string")


def test_structured_export_uses_canonical_top_level_keys() -> None:
    export = build_section_export("data/raw/Route_A_Modern/2026.pdf")
    payload = asdict(export)

    assert_true(A_INTRO in payload, "Missing canonical key A_intro")
    assert_true(A_METHODS in payload, "Missing canonical key A_methods")
    assert_true(A_RESULTS in payload, "Missing canonical key A_results")

    assert_true("sections" not in payload, "Payload must not contain nested 'sections'")
    assert_true("A_Intro" not in payload, "Payload must not contain legacy key 'A_Intro'")
    assert_true("A_Methods" not in payload, "Payload must not contain legacy key 'A_Methods'")
    assert_true("A_Results" not in payload, "Payload must not contain legacy key 'A_Results'")
    assert_true(A_TAK not in payload, "Structured export must not expose A_TAK at top level")


def run_all_tests() -> None:
    export_tests = [
        ("Modern Structured Export", "data/raw/Route_A_Modern/2026.pdf"),
        ("Legacy Structured Export", "data/raw/Route_B_Legacy/Vol1_1.pdf"),
    ]

    regression_tests = [
        ("Canonical Top-Level Keys Regression", None),
    ]

    print("=" * 72)
    print("PHASE 3 SECTION EXPORT TESTS")
    print("=" * 72)

    passed = 0
    total = len(export_tests) + len(regression_tests)

    for label, path_str in export_tests:
        try:
            test_structured_export(path_str)
            print(f"[PASS] {label}")
            passed += 1
        except Exception as exc:
            print(f"[FAIL] {label}: {exc}")

    for label, _ in regression_tests:
        try:
            test_structured_export_uses_canonical_top_level_keys()
            print(f"[PASS] {label}")
            passed += 1
        except Exception as exc:
            print(f"[FAIL] {label}: {exc}")

    print("-" * 72)
    print(f"Passed {passed}/{total} tests")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    run_all_tests()