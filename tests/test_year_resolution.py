from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bins.s04_utils.year_resolution import (
    parse_year_from_filename,
    resolve_year,
)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_manifest_year_wins() -> None:
    year = resolve_year("Vol1_1.pdf", manifest_row={"year": 1960})
    assert_true(year == 1960, "Manifest year should take precedence")


def test_modern_bare_year_filename() -> None:
    year = resolve_year("2026.pdf")
    assert_true(year == 2026, "Failed to parse bare year filename")


def test_modern_jae_pattern() -> None:
    year = resolve_year("JAE_2023_0254.pdf")
    assert_true(year == 2023, "Failed to parse JAE_YYYY_NNNN filename")


def test_legacy_map_resolution() -> None:
    year = resolve_year("Vol1_1.pdf")
    assert_true(year == 1960, "Failed to resolve year from legacy mapping CSV")


def test_parse_year_none_for_unknown_filename() -> None:
    year = parse_year_from_filename("mystery_document.pdf")
    assert_true(year is None, "Unknown filename should not parse a year")


def test_fail_fast_for_unresolved_year() -> None:
    try:
        resolve_year("mystery_document.pdf")
    except ValueError:
        return
    raise AssertionError("resolve_year() should fail for unresolved filenames")


def run_all_tests() -> None:
    tests = [
        ("Manifest Year Wins", test_manifest_year_wins),
        ("Modern Bare Year Filename", test_modern_bare_year_filename),
        ("Modern JAE Pattern", test_modern_jae_pattern),
        ("Legacy Map Resolution", test_legacy_map_resolution),
        ("Unknown Filename Parse Returns None", test_parse_year_none_for_unknown_filename),
        ("Fail Fast for Unresolved Year", test_fail_fast_for_unresolved_year),
    ]

    print("=" * 72)
    print("YEAR RESOLUTION TESTS")
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