from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from bins.s03_analysis.section_export import write_section_export


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
        "sections",
    }

    assert_true(set(data.keys()) == required_top_keys,
                "Structured JSON top-level keys mismatch")

    required_sections = {"A_TAK", "A_Intro", "A_Methods", "A_Results"}
    assert_true(set(data["sections"].keys()) == required_sections,
                "Structured JSON section keys mismatch")


def run_all_tests() -> None:

    tests = [
        ("Modern Structured Export", "data/raw/Route_A_Modern/2026.pdf"),
        ("Legacy Structured Export", "data/raw/Route_B_Legacy/Vol1_1.pdf"),
    ]

    print("=" * 72)
    print("PHASE 3 SECTION EXPORT TESTS")
    print("=" * 72)

    passed = 0

    for label, path_str in tests:
        try:
            test_structured_export(path_str)
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