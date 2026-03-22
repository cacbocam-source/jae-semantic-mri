from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Final, Iterable, cast

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from jae_legacy_acquisition_contract import (
    ABSTRACT_SNAPSHOT_ROOT,
    DOWNLOAD_PENDING,
    JOURNALS,
    PREFILL_ROOT,
    PROJECT_ROOT_DEFAULT,
    PROMOTION_PENDING,
    STATUS_CONFIRMED,
    STATUS_PENDING,
    JournalSpec,
    PrefillRecord,
    assign_route,
    derive_expected_filename,
    ensure_project_root,
    flag_doi_year_mismatch,
    make_record_id,
    normalize_doi,
    relative_raw_pdf_path,
    relative_stage_path,
    safe_filename,
    write_prefill_csv,
)

OPENALEX_WORKS_URL: Final[str] = "https://api.openalex.org/works"
DEFAULT_PER_PAGE: Final[int] = 200
DEFAULT_MAILTO: Final[str] = "research@example.edu"


def as_dict(value: Any) -> dict[str, Any]:
    return cast(dict[str, Any], value) if isinstance(value, dict) else {}


def as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    items: list[Any] = cast(list[Any], value)
    result: list[dict[str, Any]] = []

    for raw_item in items:
        if isinstance(raw_item, dict):
            result.append(cast(dict[str, Any], raw_item))

    return result

    result: list[dict[str, Any]] = []
    for raw_item in value:
        if isinstance(raw_item, dict):
            result.append(cast(dict[str, Any], raw_item))
    return result

def as_str(value: Any) -> str:
    return "" if value is None else str(value).strip()


def as_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_session() -> requests.Session:
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def reconstruct_abstract(abstract_index: Any) -> str:
    index = as_dict(abstract_index)
    if not index:
        return ""

    max_pos = -1

    for positions_value in index.values():
        if not isinstance(positions_value, list):
            continue

        positions_list: list[Any] = cast(list[Any], positions_value)
        valid_positions: list[int] = []

        for raw_pos in positions_list:
            if isinstance(raw_pos, int):
                valid_positions.append(raw_pos)

        if valid_positions:
            max_pos = max(max_pos, max(valid_positions))

    if max_pos < 0:
        return ""

    tokens: list[str] = [""] * (max_pos + 1)

    for token, positions_value in index.items():
        if not isinstance(positions_value, list):
            continue

        positions_list: list[Any] = cast(list[Any], positions_value)

        for raw_pos in positions_list:
            if isinstance(raw_pos, int) and 0 <= raw_pos < len(tokens):
                tokens[raw_pos] = str(token)

    return " ".join(token for token in tokens if token).strip()

def concepts_to_keywords(concepts_value: Any) -> tuple[str, str]:
    concepts = as_list_of_dicts(concepts_value)
    keyword_names = [as_str(c.get("display_name")) for c in concepts]
    keyword_names = [name for name in keyword_names if name]
    return ", ".join(keyword_names), json.dumps(concepts, ensure_ascii=False)


def authors_to_json(authorships_value: Any) -> str:
    authorships = as_list_of_dicts(authorships_value)
    normalized: list[dict[str, str]] = []

    for entry in authorships:
        author = as_dict(entry.get("author"))
        normalized.append(
            {
                "display_name": as_str(author.get("display_name")),
                "id": as_str(author.get("id")),
            }
        )

    return json.dumps(normalized, ensure_ascii=False)


def extract_urls(work: dict[str, Any]) -> tuple[str, str, str]:
    doi = normalize_doi(as_str(work.get("doi")))
    primary = as_dict(work.get("primary_location"))
    landing_url = as_str(primary.get("landing_page_url"))
    pdf_url = as_str(primary.get("pdf_url"))

    if pdf_url:
        return landing_url, pdf_url, "OPENALEX_PDF_URL"
    if landing_url:
        return landing_url, "", "OPENALEX_LANDING_URL"
    if doi:
        return f"https://doi.org/{doi}", "", "DOI_URL"
    return "", "", ""


def determine_review_status(*, title: str, year: int | None, best_url: str) -> str:
    if not title.strip() or year is None:
        return STATUS_PENDING
    if best_url.strip():
        return STATUS_CONFIRMED
    return STATUS_PENDING


def fetch_works_for_issn(
    *,
    session: requests.Session,
    issn: str,
    start_year: int,
    end_year: int,
    per_page: int,
    mailto: str,
    sleep_seconds: float,
    verbose_prefix: str,
) -> list[dict[str, Any]]:
    page = 1
    works: list[dict[str, Any]] = []

    while True:
        params: dict[str, str | int] = {
            "filter": (
                f"primary_location.source.issn:{issn},"
                f"publication_year:{start_year}-{end_year}"
            ),
            "per_page": per_page,
            "page": page,
            "mailto": mailto,
            "select": ",".join(
                [
                    "id",
                    "doi",
                    "display_name",
                    "publication_year",
                    "abstract_inverted_index",
                    "primary_location",
                    "concepts",
                    "authorships",
                    "biblio",
                ]
            ),
        }

        response = session.get(OPENALEX_WORKS_URL, params=params, timeout=60)
        response.raise_for_status()

        payload = as_dict(response.json())
        results = as_list_of_dicts(payload.get("results"))
        if not results:
            break

        works.extend(results)
        print(f"[{verbose_prefix}] issn={issn} page={page} cumulative_records={len(works)}")
        page += 1
        time.sleep(sleep_seconds)

    return works


def build_record(journal: JournalSpec, work: dict[str, Any], ordinal: int) -> PrefillRecord | None:
    year = as_int(work.get("publication_year"))
    if year is None:
        return None

    title = as_str(work.get("display_name"))
    if not title:
        return None

    try:
        route = assign_route(year)
    except ValueError:
        return None

    doi = normalize_doi(as_str(work.get("doi")))
    landing_url, pdf_url, url_source = extract_urls(work)
    crossref_url = f"https://doi.org/{doi}" if doi else ""

    source_identifier = ""
    if "/index.php/" in landing_url:
        source_identifier = landing_url.split("/index.php/")[-1].strip("/")
    elif as_str(work.get("id")):
        source_identifier = as_str(work.get("id")).rsplit("/", 1)[-1]

    expected_filename = derive_expected_filename(
        doi=doi,
        source_identifier=source_identifier,
        article_title=title,
    )

    best_article_url = landing_url or crossref_url
    review_status = determine_review_status(
        title=title,
        year=year,
        best_url=pdf_url or best_article_url,
    )

    keywords, concepts_json = concepts_to_keywords(work.get("concepts"))
    authors_json = authors_to_json(work.get("authorships"))

    biblio = as_dict(work.get("biblio"))
    first_page = as_str(biblio.get("first_page"))
    last_page = as_str(biblio.get("last_page"))
    pages = first_page
    if first_page and last_page:
        pages = f"{first_page}-{last_page}"

    destination_stage_path = relative_stage_path(
        route=route,
        year=year,
        expected_filename=expected_filename,
    )
    canonical_pdf_path = relative_raw_pdf_path(
        route=route,
        year=year,
        expected_filename=expected_filename,
    )

    primary = as_dict(work.get("primary_location"))
    source_location = as_str(as_dict(primary.get("source")).get("display_name"))

    notes = flag_doi_year_mismatch(
        publication_year=year,
        doi=doi,
        notes="",
    )

    return PrefillRecord(
        record_id=make_record_id(journal.code, year, ordinal),
        journal_code=journal.code,
        journal_title=journal.display_name,
        primary_issn=journal.primary_issn,
        alternate_issns=";".join(journal.alternate_issns),
        source_system="openalex",
        source_work_id=as_str(work.get("id")),
        article_title=title,
        publication_year=year,
        route=route,
        doi=doi,
        crossref_url=crossref_url,
        article_landing_url=landing_url,
        pdf_url=pdf_url,
        source_identifier=source_identifier,
        url_source=url_source,
        resolution_method="OPENALEX_METADATA",
        manual_review_status=review_status,
        download_status=DOWNLOAD_PENDING,
        promotion_status=PROMOTION_PENDING,
        expected_filename=expected_filename,
        destination_stage_path=destination_stage_path,
        staged_pdf_path="",
        canonical_pdf_path=canonical_pdf_path,
        abstract_text=reconstruct_abstract(work.get("abstract_inverted_index")),
        keyword_list=keywords,
        openalex_concepts_json=concepts_json,
        authors_json=authors_json,
        volume=as_str(biblio.get("volume")),
        issue=as_str(biblio.get("issue")),
        pages=pages,
        source_location=source_location,
        source_url=pdf_url or best_article_url,
        download_date="",
        download_http_status="",
        downloaded_bytes="",
        checksum_sha256="",
        notes=notes,
    )


def dedupe_records(records: Iterable[PrefillRecord]) -> list[PrefillRecord]:
    deduped: list[PrefillRecord] = []
    seen: set[tuple[str, str, str, int]] = set()

    for record in records:
        key = (
            record.doi.strip().lower(),
            record.article_title.strip().lower(),
            record.journal_code,
            record.publication_year,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)

    deduped.sort(
        key=lambda r: (
            r.journal_code,
            r.publication_year,
            r.article_title.lower(),
        )
    )
    return deduped


def write_jsonl(records: list[PrefillRecord], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            json.dump(record.to_row(), handle, ensure_ascii=False)
            handle.write("\n")
    return output_path


def write_abstract_snapshots(records: list[PrefillRecord], output_root: Path) -> None:
    for record in records:
        if not record.abstract_text.strip():
            continue

        target_dir = output_root / record.journal_code / str(record.publication_year)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{safe_filename(record.record_id)}.txt"

        with target_path.open("w", encoding="utf-8") as handle:
            handle.write("[METADATA_START]\n")
            handle.write(f"RECORD_ID: {record.record_id}\n")
            handle.write(f"ARTICLE_TITLE: {record.article_title}\n")
            handle.write(f"DOI: {record.doi}\n")
            handle.write(f"JOURNAL: {record.journal_code}\n")
            handle.write(f"YEAR: {record.publication_year}\n")
            handle.write(f"ROUTE: {record.route}\n")
            handle.write("[METADATA_END]\n\n")
            handle.write("[ABSTRACT_START]\n")
            handle.write(record.abstract_text)
            handle.write("\n[ABSTRACT_END]\n\n")
            handle.write("[KEYWORDS_START]\n")
            handle.write(record.keyword_list)
            handle.write("\n[KEYWORDS_END]\n")


def select_journals(requested_codes: list[str]) -> list[JournalSpec]:
    if not requested_codes:
        return list(JOURNALS)

    requested = {code.upper().strip() for code in requested_codes}
    selected = [journal for journal in JOURNALS if journal.code in requested]
    missing = sorted(requested - {j.code for j in selected})
    if missing:
        raise ValueError(f"Unknown journal codes: {missing}")
    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Harvest OpenAlex metadata into a JAE_Legacy_Audit-aligned prefill "
            "queue for downstream DOI/OJS resolution and download."
        )
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--start-year", type=int, required=True)
    parser.add_argument("--end-year", type=int, required=True)
    parser.add_argument("--journal-codes", nargs="*", default=[])
    parser.add_argument("--per-page", type=int, default=DEFAULT_PER_PAGE)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--mailto", type=str, default=DEFAULT_MAILTO)
    parser.add_argument("--write-abstract-snapshots", action="store_true")
    parser.add_argument(
        "--output-stem",
        type=str,
        default="legacy_metadata_prefill",
        help="Filename stem for CSV and JSONL outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.start_year > args.end_year:
        raise ValueError("--start-year must be <= --end-year")

    project_root = ensure_project_root(args.project_root)
    session = build_session()
    selected_journals = select_journals(args.journal_codes)

    harvested: list[PrefillRecord] = []
    for journal in selected_journals:
        works_by_source: list[dict[str, Any]] = []

        for issn in journal.all_issns:
            works_by_source.extend(
                fetch_works_for_issn(
                    session=session,
                    issn=issn,
                    start_year=args.start_year,
                    end_year=args.end_year,
                    per_page=args.per_page,
                    mailto=args.mailto,
                    sleep_seconds=args.sleep_seconds,
                    verbose_prefix=journal.code,
                )
            )

        ordinal = 1
        for work in works_by_source:
            record = build_record(journal, work, ordinal)
            if record is None:
                continue
            harvested.append(record)
            ordinal += 1

    harvested = dedupe_records(harvested)

    output_dir = project_root / PREFILL_ROOT
    stem = f"{args.output_stem}_{args.start_year}_{args.end_year}"
    csv_path = output_dir / f"{stem}.csv"
    jsonl_path = output_dir / f"{stem}.jsonl"

    write_prefill_csv(harvested, csv_path)
    write_jsonl(harvested, jsonl_path)

    if args.write_abstract_snapshots:
        write_abstract_snapshots(harvested, project_root / ABSTRACT_SNAPSHOT_ROOT)

    print(f"Wrote CSV:   {csv_path}")
    print(f"Wrote JSONL: {jsonl_path}")
    print(f"Records:     {len(harvested)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())