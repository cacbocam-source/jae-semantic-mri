from __future__ import annotations

import argparse
import csv
from pathlib import Path

from jae_legacy_acquisition_contract import (
    PIPELINE_MANIFEST_COLUMNS,
    PIPELINE_MANIFEST_PATH,
    PROJECT_ROOT_DEFAULT,
    PrefillRecord,
    ensure_project_root,
    make_pipeline_doc_id,
    read_prefill_csv,
    resolve_under_project_root,
    utc_now_iso,
)


def read_manifest_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=PIPELINE_MANIFEST_COLUMNS)
            writer.writeheader()

    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_manifest_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PIPELINE_MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def prefill_to_manifest_row(
    record: PrefillRecord,
    canonical_abs_path: Path,
) -> dict[str, str]:
    doc_id = make_pipeline_doc_id(
        route=record.route,
        year=record.publication_year,
        canonical_pdf_path=str(canonical_abs_path),
    )

    return {
        "doc_id": doc_id,
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
        "last_stage_run": "",
        "artifact_version": "1.0",
        "updated_at": utc_now_iso(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bridge promoted prefill rows into data/manifests/pipeline_manifest.csv."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--csv-path", type=Path, required=True)
    parser.add_argument("--manifest-path", type=Path, default=PIPELINE_MANIFEST_PATH)
    args = parser.parse_args(argv)

    project_root = ensure_project_root(args.project_root)
    prefill_rows = read_prefill_csv(args.csv_path.resolve())
    manifest_path = resolve_under_project_root(project_root, str(args.manifest_path))
    manifest_rows = read_manifest_rows(manifest_path)

    by_source_path = {row.get("source_pdf_path", ""): row for row in manifest_rows}
    by_doc_id = {row.get("doc_id", ""): row for row in manifest_rows}

    added = 0
    updated = 0
    skipped = 0

    for record in prefill_rows:
        if record.promotion_status != "promoted":
            skipped += 1
            continue

        if not str(record.canonical_pdf_path).strip():
            print(f"[SKIP] {record.record_id}: missing canonical_pdf_path")
            skipped += 1
            continue

        canonical_abs = resolve_under_project_root(
            project_root, record.canonical_pdf_path
        )

        if not canonical_abs.exists():
            print(f"[SKIP] {record.record_id}: canonical file missing -> {canonical_abs}")
            skipped += 1
            continue

        candidate = prefill_to_manifest_row(record, canonical_abs)

        existing = by_source_path.get(candidate["source_pdf_path"])
        if existing is None:
            existing = by_doc_id.get(candidate["doc_id"])

        if existing is None:
            manifest_rows.append(candidate)
            by_source_path[candidate["source_pdf_path"]] = candidate
            by_doc_id[candidate["doc_id"]] = candidate
            added += 1
            print(f"[ADD] {candidate['doc_id']} -> {candidate['source_pdf_path']}")
            continue

        existing.update(
            {
                "source_pdf_path": candidate["source_pdf_path"],
                "source_filename": candidate["source_filename"],
                "route": candidate["route"],
                "year": candidate["year"],
                "updated_at": utc_now_iso(),
            }
        )
        updated += 1
        print(f"[UPDATE] {existing['doc_id']} -> {existing['source_pdf_path']}")

    write_manifest_rows(manifest_path, manifest_rows)
    print(
        f"Updated manifest: {manifest_path} | added={added} updated={updated} skipped={skipped}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())