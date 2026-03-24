from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from config import END_YEAR, MANIFEST_DIR, START_YEAR

JAE_FILENAME_RE = re.compile(r"^JAE_(?P<year>\d{4})_\d+\.pdf$", re.IGNORECASE)
STANDALONE_YEAR_RE = re.compile(r"(?<!\d)(?P<year>\d{4})(?!\d)")
DIRECTORY_YEAR_RE = re.compile(r"^(?P<year>(19|20)\d{2})$")

LEGACY_YEAR_MAP_PATH = MANIFEST_DIR / "legacy_filename_year_map.csv"


def _validate_year(year: int) -> int:
    if year < START_YEAR or year > END_YEAR:
        raise ValueError(
            f"Resolved year {year} is outside configured range "
            f"{START_YEAR}–{END_YEAR}."
        )
    return year


def _coerce_year(value: Any) -> int:
    text = str(value).strip()
    if not text:
        raise ValueError("Year value is empty.")
    return _validate_year(int(text))


@lru_cache(maxsize=1)
def load_legacy_year_map() -> dict[str, int]:
    """
    Load explicit legacy filename → year mappings from CSV.

    CSV schema:
        source_filename,year
        Vol1_1.pdf,1960
    """
    if not LEGACY_YEAR_MAP_PATH.exists():
        return {}

    mapping: dict[str, int] = {}

    with LEGACY_YEAR_MAP_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = {"source_filename", "year"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(
                f"{LEGACY_YEAR_MAP_PATH} must contain columns: {sorted(required)}"
            )

        for row in reader:
            filename = str(row["source_filename"]).strip()
            if not filename:
                raise ValueError(
                    f"{LEGACY_YEAR_MAP_PATH} contains an empty source_filename value."
                )

            if filename in mapping:
                raise ValueError(
                    f"{LEGACY_YEAR_MAP_PATH} contains a duplicate mapping for: {filename}"
                )

            mapping[filename] = _coerce_year(row["year"])

    return mapping


def parse_year_from_filename(filename: str) -> int | None:
    """
    Parse year from supported filename conventions.

    Supported forms:
    - JAE_YYYY_NNNN.pdf
    - YYYY.pdf
    - any filename containing a single valid standalone 4-digit year

    Returns:
        int | None
    """
    basename = Path(filename).name

    match = JAE_FILENAME_RE.match(basename)
    if match:
        return _validate_year(int(match.group("year")))

    candidates = [
        int(match.group("year"))
        for match in STANDALONE_YEAR_RE.finditer(basename)
    ]

    valid = [year for year in candidates if START_YEAR <= year <= END_YEAR]

    if len(valid) == 1:
        return valid[0]

    if len(valid) > 1:
        raise ValueError(
            f"Filename {basename!r} contains multiple candidate years: {valid}"
        )

    return None


def parse_year_from_parent_directories(source_path: str | Path) -> int | None:
    """
    Parse year from parent directory names, nearest parent first.

    Supported form:
    - .../<YEAR>/<filename>.pdf

    Returns:
        int | None
    """
    path = Path(source_path).expanduser()

    for parent in path.parents:
        match = DIRECTORY_YEAR_RE.fullmatch(parent.name.strip())
        if match:
            return _validate_year(int(match.group("year")))

    return None


def resolve_year(
    source_path: str | Path,
    manifest_row: Mapping[str, Any] | None = None,
) -> int:
    """
    Resolve publication year using deterministic precedence:

    1. manifest_row['year'] if provided
    2. explicit legacy filename map
    3. supported filename parsing
    4. supported parent-directory parsing
    5. fail fast if unresolved
    """
    if manifest_row is not None:
        manifest_year = manifest_row.get("year")
        if manifest_year is not None and str(manifest_year).strip():
            return _coerce_year(manifest_year)

    path = Path(source_path).expanduser()
    filename = path.name

    legacy_map = load_legacy_year_map()
    if filename in legacy_map:
        return legacy_map[filename]

    parsed = parse_year_from_filename(filename)
    if parsed is not None:
        return parsed

    parent_parsed = parse_year_from_parent_directories(path)
    if parent_parsed is not None:
        return parent_parsed

    raise ValueError(
        f"Unable to resolve year for {filename!r}. "
        f"Provide manifest year or add an explicit mapping to "
        f"{LEGACY_YEAR_MAP_PATH.name}."
    )


__all__ = [
    "LEGACY_YEAR_MAP_PATH",
    "load_legacy_year_map",
    "parse_year_from_filename",
    "parse_year_from_parent_directories",
    "resolve_year",
]