from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

from bins.s01_ingest.ledger import make_doc_id
from legacy_acquisition.jae_legacy_acquisition_contract import (
    PROMOTION_PROMOTED,
    PrefillRecord,
    read_prefill_csv,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_MANIFEST_PATH = REPO_ROOT / "data" / "manifests" / "pipeline_manifest.csv"


def resolve_under_project_root(project_root: Path, candidate: str | Path) -> Path:
    path = Path(candidate)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def read_manifest_header(path: Path) -> list[str]:
    if path.exists():
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
        if header:
            return header

    raise ValueError(
        f"Unable to read manifest header from {path}. "
        "The pipeline manifest must already exist and contain a header row."
    )


def read_manifest_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    fieldnames = read_manifest_header(path)

    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    return fieldnames, rows


def write_manifest_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _empty_manifest_row(fieldnames: list[str]) -> dict[str, str]:
    return {column: "" for column in fieldnames}


def prefill_to_manifest_row(
    record: PrefillRecord,
    canonical_abs_path: Path,
    fieldnames: list[str],
) -> dict[str, str]:
    """
    Convert a promoted prefill record into a pipeline manifest row using the
    canonical pipeline doc_id contract (make_doc_id on the canonical PDF path).
    """
    row = _empty_manifest_row(fieldnames)

    base_values = {
        "doc_id": make_doc_id(canonical_abs_path),
        "source_pdf_path": str(canonical_abs_path),
        "source_filename": canonical_abs_path.name,
        "route": record.route,
        "year": str(record.publication_year),
        "extract_status": "pending",
        "structured_status": "pending",
        "embedding_status": "pending",
        "metrics_status": "pending",
        "extract_method": "",
        "page_count": "",
        "error_message": "",
        "last_stage_run": "manifest_bridge",
        "artifact_version": "1.0",
        "updated_at": "",
    }

    for key, value in base_values.items():
        if key in row:
            row[key] = value

    return row


def iter_promoted_records(prefill_rows: Iterable[PrefillRecord]) -> Iterable[PrefillRecord]:
    for record in prefill_rows:
        if record.promotion_status == PROMOTION_PROMOTED:
            yield record


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bridge promoted prefill rows into data/manifests/pipeline_manifest.csv."
    )
    parser.add_argument("--project-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--csv-path", type=Path, required=True)
    parser.add_argument("--manifest-path", type=Path, default=PIPELINE_MANIFEST_PATH)
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    prefill_rows = read_prefill_csv(args.csv_path.resolve())
    manifest_path = resolve_under_project_root(project_root, str(args.manifest_path))
    fieldnames, manifest_rows = read_manifest_rows(manifest_path)

    by_source_path = {
        row.get("source_pdf_path", ""): row
        for row in manifest_rows
        if row.get("source_pdf_path", "")
    }
    by_doc_id = {
        row.get("doc_id", ""): row
        for row in manifest_rows
        if row.get("doc_id", "")
    }

    added = 0
    updated = 0
    skipped = 0

    for record in iter_promoted_records(prefill_rows):
        canonical_abs = resolve_under_project_root(project_root, record.canonical_pdf_path)
        candidate = prefill_to_manifest_row(record, canonical_abs, fieldnames)

        existing = by_source_path.get(candidate.get("source_pdf_path", ""))
        if existing is None:
            existing = by_doc_id.get(candidate.get("doc_id", ""))

        if existing is None:
            manifest_rows.append(candidate)
            if candidate.get("source_pdf_path", ""):
                by_source_path[candidate["source_pdf_path"]] = candidate
            if candidate.get("doc_id", ""):
                by_doc_id[candidate["doc_id"]] = candidate
            added += 1
            print(f"[ADD] {candidate.get('doc_id', '')} -> {candidate.get('source_pdf_path', '')}")
            continue

        changed = False
        for key in fieldnames:
            new_value = candidate.get(key, "")

            if key == "doc_id" and existing.get("doc_id", "") and existing.get("doc_id", "") != new_value:
                # Preserve any existing canonical doc_id if already present.
                continue

            if new_value and existing.get(key, "") != new_value:
                existing[key] = new_value
                changed = True

        if changed:
            updated += 1
            print(
                "[UPDATE] "
                f"{existing.get('doc_id', '')} -> "
                f"{existing.get('source_filename', '')} | "
                f"{existing.get('route', '')} | "
                f"{existing.get('year', '')}"
            )
        else:
            skipped += 1
            print(f"[SKIP] {existing.get('doc_id', '')} -> {existing.get('source_pdf_path', '')}")

    write_manifest_rows(manifest_path, fieldnames, manifest_rows)
    print(
        f"Updated manifest: {manifest_path} | "
        f"added={added} updated={updated} skipped={skipped}"
    )


if __name__ == "__main__":
    main()
