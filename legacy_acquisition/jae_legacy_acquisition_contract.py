from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, cast

PROJECT_ROOT_DEFAULT: Final[Path] = Path(
    "/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit"
)
PREFILL_ROOT: Final[Path] = Path("data/staging/metadata_prefill")
ABSTRACT_SNAPSHOT_ROOT: Final[Path] = Path(
    "data/staging/metadata_prefill/abstract_snapshots"
)
DOWNLOAD_STAGING_ROOT: Final[Path] = Path("data/staging/legacy_prefill_downloads")
RAW_PDF_ROOT: Final[Path] = Path("data/raw")
PIPELINE_MANIFEST_PATH: Final[Path] = Path("data/manifests/pipeline_manifest.csv")

ROUTE_MODERN: Final[str] = "Route_A_Modern"
ROUTE_LEGACY: Final[str] = "Route_B_Legacy"
VALID_ROUTES: Final[frozenset[str]] = frozenset({ROUTE_MODERN, ROUTE_LEGACY})

LEGACY_CUTOFF: Final[int] = 2000
PROJECT_YEAR_MIN: Final[int] = 1960
PROJECT_YEAR_MAX: Final[int] = 2026

STATUS_PENDING: Final[str] = "pending"
STATUS_CONFIRMED: Final[str] = "confirmed"
STATUS_REJECTED: Final[str] = "rejected"

DOWNLOAD_PENDING: Final[str] = "pending"
DOWNLOAD_DOWNLOADED: Final[str] = "downloaded"
DOWNLOAD_FAILED: Final[str] = "failed"
DOWNLOAD_SKIPPED: Final[str] = "skipped"

PROMOTION_PENDING: Final[str] = "pending"
PROMOTION_APPROVED: Final[str] = "approved"
PROMOTION_PROMOTED: Final[str] = "promoted"
PROMOTION_SKIPPED: Final[str] = "skipped"

SAFE_FILENAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"[^A-Za-z0-9._-]+")
DOI_URL_PATTERN: Final[re.Pattern[str]] = re.compile(r"^https?://doi\.org/", re.I)
DOI_YEAR_PATTERN: Final[re.Pattern[str]] = re.compile(r"(19\d{2}|20\d{2})")

PIPELINE_MANIFEST_COLUMNS: Final[tuple[str, ...]] = (
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

PREFILL_FIELDNAMES: Final[tuple[str, ...]] = (
    "record_id",
    "journal_code",
    "journal_title",
    "primary_issn",
    "alternate_issns",
    "source_system",
    "source_work_id",
    "article_title",
    "publication_year",
    "route",
    "doi",
    "crossref_url",
    "article_landing_url",
    "pdf_url",
    "source_identifier",
    "url_source",
    "resolution_method",
    "manual_review_status",
    "download_status",
    "promotion_status",
    "expected_filename",
    "destination_stage_path",
    "staged_pdf_path",
    "canonical_pdf_path",
    "abstract_text",
    "keyword_list",
    "openalex_concepts_json",
    "authors_json",
    "volume",
    "issue",
    "pages",
    "source_location",
    "source_url",
    "download_date",
    "download_http_status",
    "downloaded_bytes",
    "checksum_sha256",
    "notes",
)


@dataclass(frozen=True)
class JournalSpec:
    code: str
    display_name: str
    primary_issn: str
    alternate_issns: tuple[str, ...] = ()
    notes: str = ""

    @property
    def all_issns(self) -> tuple[str, ...]:
        values = [self.primary_issn, *self.alternate_issns]
        return tuple(v for v in values if v)


JOURNALS: Final[tuple[JournalSpec, ...]] = (
    JournalSpec(
        code="JAE",
        display_name="Journal of Agricultural Education",
        primary_issn="1042-0541",
        alternate_issns=("0002-7480",),
        notes="Primary target journal for JAE_Legacy_Audit.",
    ),
    JournalSpec(
        code="AAD",
        display_name="Advancements in Agricultural Development",
        primary_issn="2692-0034",
        alternate_issns=("2690-5078",),
        notes="Inventory conflict observed across legacy scripts; keep both ISSNs.",
    ),
    JournalSpec(
        code="NACTA",
        display_name="NACTA Journal",
        primary_issn="0149-4910",
    ),
    JournalSpec(
        code="JOLE",
        display_name="Journal of Leadership Education",
        primary_issn="1552-9045",
    ),
    JournalSpec(
        code="JAC",
        display_name="Journal of Applied Communications",
        primary_issn="1553-6157",
        alternate_issns=("1051-0834",),
        notes="Inventory conflict observed across legacy scripts; keep both ISSNs.",
    ),
    JournalSpec(
        code="JRS",
        display_name="Rural Sociology",
        primary_issn="0036-0112",
    ),
    JournalSpec(
        code="SR",
        display_name="Sociologia Ruralis",
        primary_issn="0038-0199",
    ),
)


@dataclass
class PrefillRecord:
    record_id: str
    journal_code: str = ""
    journal_title: str = ""
    primary_issn: str = ""
    alternate_issns: str = ""
    source_system: str = ""
    source_work_id: str = ""
    article_title: str = ""
    publication_year: int = 0
    route: str = ""
    doi: str = ""
    crossref_url: str = ""
    article_landing_url: str = ""
    pdf_url: str = ""
    source_identifier: str = ""
    url_source: str = ""
    resolution_method: str = ""
    manual_review_status: str = STATUS_PENDING
    download_status: str = DOWNLOAD_PENDING
    promotion_status: str = PROMOTION_PENDING
    expected_filename: str = ""
    destination_stage_path: str = ""
    staged_pdf_path: str = ""
    canonical_pdf_path: str = ""
    abstract_text: str = ""
    keyword_list: str = ""
    openalex_concepts_json: str = ""
    authors_json: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    source_location: str = ""
    source_url: str = ""
    download_date: str = ""
    download_http_status: str = ""
    downloaded_bytes: str = ""
    checksum_sha256: str = ""
    notes: str = ""

    def to_row(self) -> dict[str, str]:
        row: dict[str, str] = {}
        for key, value in asdict(self).items():
            row[key] = "" if value is None else str(value)
        return row

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "PrefillRecord":
        year_raw = (row.get("publication_year") or "").strip()
        try:
            publication_year = int(year_raw) if year_raw else 0
        except ValueError:
            publication_year = 0

        return cls(
            record_id=row.get("record_id", ""),
            journal_code=row.get("journal_code", ""),
            journal_title=row.get("journal_title", ""),
            primary_issn=row.get("primary_issn", ""),
            alternate_issns=row.get("alternate_issns", ""),
            source_system=row.get("source_system", ""),
            source_work_id=row.get("source_work_id", ""),
            article_title=row.get("article_title", ""),
            publication_year=publication_year,
            route=row.get("route", ""),
            doi=row.get("doi", ""),
            crossref_url=row.get("crossref_url", ""),
            article_landing_url=row.get("article_landing_url", ""),
            pdf_url=row.get("pdf_url", ""),
            source_identifier=row.get("source_identifier", ""),
            url_source=row.get("url_source", ""),
            resolution_method=row.get("resolution_method", ""),
            manual_review_status=row.get("manual_review_status", STATUS_PENDING),
            download_status=row.get("download_status", DOWNLOAD_PENDING),
            promotion_status=row.get("promotion_status", PROMOTION_PENDING),
            expected_filename=row.get("expected_filename", ""),
            destination_stage_path=row.get("destination_stage_path", ""),
            staged_pdf_path=row.get("staged_pdf_path", ""),
            canonical_pdf_path=row.get("canonical_pdf_path", ""),
            abstract_text=row.get("abstract_text", ""),
            keyword_list=row.get("keyword_list", ""),
            openalex_concepts_json=row.get("openalex_concepts_json", ""),
            authors_json=row.get("authors_json", ""),
            volume=row.get("volume", ""),
            issue=row.get("issue", ""),
            pages=row.get("pages", ""),
            source_location=row.get("source_location", ""),
            source_url=row.get("source_url", ""),
            download_date=row.get("download_date", ""),
            download_http_status=row.get("download_http_status", ""),
            downloaded_bytes=row.get("downloaded_bytes", ""),
            checksum_sha256=row.get("checksum_sha256", ""),
            notes=row.get("notes", ""),
        )


def append_note(existing: str, new_note: str) -> str:
    existing = (existing or "").strip()
    new_note = (new_note or "").strip()
    if not new_note:
        return existing
    if not existing:
        return new_note
    if new_note in existing:
        return existing
    return f"{existing} | {new_note}"


def extract_year_from_doi(doi: str) -> int | None:
    doi = (doi or "").strip()
    if not doi:
        return None
    matches = DOI_YEAR_PATTERN.findall(doi)
    if not matches:
        return None
    try:
        return int(matches[0])
    except ValueError:
        return None


def flag_doi_year_mismatch(
    *,
    publication_year: int | str | None,
    doi: str,
    notes: str = "",
) -> str:
    if publication_year in (None, ""):
        return notes

    try:
        pub_year = int(str(publication_year).strip())
    except ValueError:
        return notes

    doi_year = extract_year_from_doi(doi)
    if doi_year is None:
        return notes

    if doi_year != pub_year:
        return append_note(
            notes,
            f"DOI_YEAR_MISMATCH: DOI token year ({doi_year}) conflicts with publication year ({pub_year}); publication year retained from source metadata/citation.",
        )

    return notes


def ensure_project_root(project_root: Path) -> Path:
    resolved = project_root.resolve()
    if resolved != PROJECT_ROOT_DEFAULT:
        raise ValueError(
            f"Project root mismatch. Expected {PROJECT_ROOT_DEFAULT}, got {resolved}"
        )
    return resolved


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def validate_year(year: int) -> None:
    if year < PROJECT_YEAR_MIN or year > PROJECT_YEAR_MAX:
        raise ValueError(
            f"Year out of supported bounds: {year} "
            f"(expected {PROJECT_YEAR_MIN}..{PROJECT_YEAR_MAX})"
        )


def assign_route(year: int) -> str:
    validate_year(year)
    return ROUTE_MODERN if year >= LEGACY_CUTOFF else ROUTE_LEGACY


def safe_filename(value: str, *, default: str = "untitled") -> str:
    cleaned = SAFE_FILENAME_PATTERN.sub("_", value.strip())
    cleaned = cleaned.strip("._")
    return cleaned or default


def normalize_doi(doi_value: str | None) -> str:
    if not doi_value:
        return ""
    value = DOI_URL_PATTERN.sub("", doi_value.strip())
    return value.strip()


def normalize_doi_filename(doi: str) -> str:
    value = safe_filename(doi.replace("/", "_"), default="no_doi")
    return value + ".pdf"


def derive_expected_filename(
    *,
    doi: str,
    source_identifier: str,
    article_title: str,
) -> str:
    if doi.strip():
        return normalize_doi_filename(doi)
    if source_identifier.strip():
        return (
            safe_filename(
                source_identifier.replace("/", "_"),
                default="source_identifier",
            )
            + ".pdf"
        )
    return safe_filename(article_title[:120], default="article") + ".pdf"


def relative_stage_path(*, route: str, year: int, expected_filename: str) -> str:
    return str(DOWNLOAD_STAGING_ROOT / route / str(year) / expected_filename)


def relative_raw_pdf_path(*, route: str, year: int, expected_filename: str) -> str:
    return str(RAW_PDF_ROOT / route / str(year) / expected_filename)


def resolve_under_project_root(project_root: Path, relative_or_absolute: str) -> Path:
    path = Path(relative_or_absolute)
    if path.is_absolute():
        return path
    return project_root / path


def make_record_id(journal_code: str, year: int, ordinal: int) -> str:
    return f"{journal_code}_{year}_{ordinal:05d}"


def make_pipeline_doc_id(*, route: str, year: int, canonical_pdf_path: str) -> str:
    route_token = "modern" if route == ROUTE_MODERN else "legacy"
    digest = hashlib.sha1(canonical_pdf_path.encode("utf-8")).hexdigest()[:10]
    return f"jae_{route_token}_{year}_{digest}"


def read_prefill_csv(csv_path: Path) -> list[PrefillRecord]:
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [PrefillRecord.from_row(row) for row in rows]


def write_prefill_csv(records: list[PrefillRecord], csv_path: Path) -> Path:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PREFILL_FIELDNAMES)
        writer.writeheader()
        for record in records:
            row = record.to_row()
            writer.writerow(cast(Any, row))
    return csv_path