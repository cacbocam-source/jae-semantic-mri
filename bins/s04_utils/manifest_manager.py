from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Iterable

from config import MANIFEST_DIR

PIPELINE_MANIFEST = MANIFEST_DIR / "pipeline_manifest.csv"

STAGE_COLUMNS = (
    "extract_status",
    "structured_status",
    "embedding_status",
    "metrics_status",
)

STATUS_PENDING = "pending"
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"

MANIFEST_COLUMNS = (
    "doc_id",
    "source_pdf_path",
    "source_filename",
    "route",
    "year",
    "extract_status",
    "structured_status",
    "embedding_status",
    "metrics_status",
    "extract_method",
    "page_count",
    "error_message",
    "last_stage_run",
    "artifact_version",
    "updated_at",
)


@dataclass(frozen=True)
class ManifestRecord:
    doc_id: str
    source_pdf_path: str
    source_filename: str
    route: str
    year: str
    extract_status: str = STATUS_PENDING
    structured_status: str = STATUS_PENDING
    embedding_status: str = STATUS_PENDING
    metrics_status: str = STATUS_PENDING
    extract_method: str = ""
    page_count: str = ""
    error_message: str = ""
    last_stage_run: str = ""
    artifact_version: str = "1.0"
    updated_at: str = ""

    def to_row(self) -> dict[str, str]:
        row = {key: str(value) for key, value in asdict(self).items()}
        if not row["updated_at"]:
            row["updated_at"] = utc_now_iso()
        return row


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def ensure_manifest_exists(manifest_path: Path = PIPELINE_MANIFEST) -> Path:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if not manifest_path.exists():
        with manifest_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
            writer.writeheader()
    return manifest_path


def load_manifest_rows(manifest_path: Path = PIPELINE_MANIFEST) -> list[dict[str, str]]:
    ensure_manifest_exists(manifest_path)
    with manifest_path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_manifest_rows(
    rows: list[dict[str, str]],
    manifest_path: Path = PIPELINE_MANIFEST,
) -> None:
    ensure_manifest_exists(manifest_path)
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)  # pyright: ignore[reportArgumentType]


def upsert_record(
    record: ManifestRecord,
    manifest_path: Path = PIPELINE_MANIFEST,
) -> None:
    rows = load_manifest_rows(manifest_path)
    row = record.to_row()

    replaced = False
    for idx, existing in enumerate(rows):
        if existing["doc_id"] == row["doc_id"]:
            merged = existing.copy()
            merged.update({k: v for k, v in row.items() if v != ""})
            merged["updated_at"] = utc_now_iso()
            rows[idx] = merged
            replaced = True
            break

    if not replaced:
        rows.append(row)

    write_manifest_rows(rows, manifest_path)


def mark_stage_success(
    doc_id: str,
    stage: str,
    *,
    extract_method: str = "",
    page_count: str = "",
    manifest_path: Path = PIPELINE_MANIFEST,
) -> None:
    _update_stage(
        doc_id,
        stage,
        STATUS_SUCCESS,
        extract_method=extract_method,
        page_count=page_count,
        error_message="",
        manifest_path=manifest_path,
    )


def mark_stage_failure(
    doc_id: str,
    stage: str,
    error_message: str,
    manifest_path: Path = PIPELINE_MANIFEST,
) -> None:
    _update_stage(
        doc_id,
        stage,
        STATUS_FAILED,
        error_message=error_message,
        manifest_path=manifest_path,
    )


def mark_stage_skipped(
    doc_id: str,
    stage: str,
    error_message: str = "",
    manifest_path: Path = PIPELINE_MANIFEST,
) -> None:
    _update_stage(
        doc_id,
        stage,
        STATUS_SKIPPED,
        error_message=error_message,
        manifest_path=manifest_path,
    )


def _update_stage(
    doc_id: str,
    stage: str,
    status: str,
    *,
    extract_method: str = "",
    page_count: str = "",
    error_message: str = "",
    manifest_path: Path = PIPELINE_MANIFEST,
) -> None:
    if stage not in STAGE_COLUMNS:
        raise ValueError(f"Unknown stage: {stage}")

    rows = load_manifest_rows(manifest_path)
    found = False

    for row in rows:
        if row["doc_id"] == doc_id:
            row[stage] = status
            row["last_stage_run"] = stage
            row["updated_at"] = utc_now_iso()
            row["error_message"] = error_message
            if extract_method:
                row["extract_method"] = extract_method
            if page_count:
                row["page_count"] = page_count
            found = True
            break

    if not found:
        raise ValueError(f"doc_id not found in manifest: {doc_id}")

    write_manifest_rows(rows, manifest_path)


def get_pending_records(
    stage: str,
    manifest_path: Path = PIPELINE_MANIFEST,
) -> list[dict[str, str]]:
    if stage not in STAGE_COLUMNS:
        raise ValueError(f"Unknown stage: {stage}")

    rows = load_manifest_rows(manifest_path)
    return [row for row in rows if row.get(stage, STATUS_PENDING) != STATUS_SUCCESS]


def seed_manifest_from_raw_pdfs(
    pdf_paths: Iterable[Path],
    *,
    infer_route: Callable[[Path], str],
    infer_year: Callable[[Path], int],
    make_doc_id: Callable[[Path], str],
    manifest_path: Path = PIPELINE_MANIFEST,
) -> None:
    ensure_manifest_exists(manifest_path)

    for pdf_path in pdf_paths:
        record = ManifestRecord(
            doc_id=make_doc_id(pdf_path),
            source_pdf_path=str(pdf_path.resolve()),
            source_filename=pdf_path.name,
            route=infer_route(pdf_path),
            year=str(infer_year(pdf_path)),
        )
        upsert_record(record, manifest_path)