from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[1]

MANIFEST_PATH = REPO_ROOT / "data" / "manifests" / "pipeline_manifest.csv"
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "Route_A_Modern"
STRUCTURED_DIR = REPO_ROOT / "data" / "structured" / "Route_A_Modern"
EMBEDDINGS_DIR = REPO_ROOT / "data" / "embeddings" / "Route_A_Modern"

ROUTE_NAME = "Route_A_Modern"
DEFAULT_START_YEAR = 2000


def normalize_status(value: str) -> str:
    return (value or "").strip().lower()


def infer_year(row: dict) -> int | None:
    raw = str(row.get("year", "")).strip()
    if raw.isdigit() and len(raw) == 4:
        return int(raw)

    source_filename = str(row.get("source_filename", "")).strip()
    stem = Path(source_filename).stem
    prefix = stem.split("_", 1)[0]
    if prefix.isdigit() and len(prefix) == 4:
        return int(prefix)

    return None


def epoch_label(year: int) -> str:
    start = year - ((year - DEFAULT_START_YEAR) % 5)
    return f"{start}-{start + 4}"


@dataclass
class RouteADoc:
    doc_id: str
    source_filename: str
    year: int
    epoch: str
    route: str
    extract_status: str
    structured_status: str
    embedding_status: str
    metrics_status: str
    processed_present: bool
    structured_present: bool
    embedding_present: bool

    @property
    def upstream_complete(self) -> bool:
        return (
            self.extract_status == "success"
            and self.structured_status == "success"
            and self.embedding_status == "success"
            and self.processed_present
            and self.structured_present
            and self.embedding_present
        )


def _processed_stems() -> set[str]:
    return {p.stem for p in PROCESSED_DIR.rglob("*.txt")} if PROCESSED_DIR.exists() else set()


def _structured_stems() -> set[str]:
    return {p.stem for p in STRUCTURED_DIR.rglob("*.json")} if STRUCTURED_DIR.exists() else set()


def _embedding_doc_ids() -> set[str]:
    return {p.stem for p in EMBEDDINGS_DIR.rglob("*.npz")} if EMBEDDINGS_DIR.exists() else set()


def load_route_a_docs(start_year: int = DEFAULT_START_YEAR) -> List[RouteADoc]:
    processed = _processed_stems()
    structured = _structured_stems()
    embedded = _embedding_doc_ids()

    docs: List[RouteADoc] = []

    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        if str(row.get("route", "")).strip() != ROUTE_NAME:
            continue

        year = infer_year(row)
        if year is None or year < start_year:
            continue

        source_filename = str(row.get("source_filename", "")).strip()
        stem = Path(source_filename).stem
        doc_id = str(row.get("doc_id", "")).strip()

        docs.append(
            RouteADoc(
                doc_id=doc_id,
                source_filename=source_filename,
                year=year,
                epoch=epoch_label(year),
                route=ROUTE_NAME,
                extract_status=normalize_status(row.get("extract_status", "")),
                structured_status=normalize_status(row.get("structured_status", "")),
                embedding_status=normalize_status(row.get("embedding_status", "")),
                metrics_status=normalize_status(row.get("metrics_status", "")),
                processed_present=stem in processed,
                structured_present=stem in structured,
                embedding_present=doc_id in embedded if doc_id else False,
            )
        )

    docs.sort(key=lambda d: (d.year, d.source_filename, d.doc_id))
    return docs


def summarize_by_year(docs: Iterable[RouteADoc]) -> List[dict]:
    bucket: Dict[int, dict] = defaultdict(
        lambda: {
            "doc_count": 0,
            "upstream_complete_count": 0,
            "extract_success_count": 0,
            "structured_success_count": 0,
            "embedding_success_count": 0,
            "metrics_success_count": 0,
            "processed_present_count": 0,
            "structured_present_count": 0,
            "embedding_present_count": 0,
        }
    )

    for d in docs:
        b = bucket[d.year]
        b["doc_count"] += 1
        b["upstream_complete_count"] += int(d.upstream_complete)
        b["extract_success_count"] += int(d.extract_status == "success")
        b["structured_success_count"] += int(d.structured_status == "success")
        b["embedding_success_count"] += int(d.embedding_status == "success")
        b["metrics_success_count"] += int(d.metrics_status == "success")
        b["processed_present_count"] += int(d.processed_present)
        b["structured_present_count"] += int(d.structured_present)
        b["embedding_present_count"] += int(d.embedding_present)

    rows = []
    if not bucket:
        return rows

    min_year = min(bucket)
    max_year = max(bucket)

    for year in range(min_year, max_year + 1):
        epoch = epoch_label(year)
        if year not in bucket:
            rows.append(
                {
                    "year": year,
                    "epoch": epoch,
                    "status": "missing",
                    "doc_count": 0,
                    "upstream_complete_count": 0,
                    "extract_success_count": 0,
                    "structured_success_count": 0,
                    "embedding_success_count": 0,
                    "metrics_success_count": 0,
                    "processed_present_count": 0,
                    "structured_present_count": 0,
                    "embedding_present_count": 0,
                }
            )
            continue

        b = bucket[year]
        rows.append(
            {
                "year": year,
                "epoch": epoch,
                "status": "covered",
                **b,
            }
        )

    return rows
