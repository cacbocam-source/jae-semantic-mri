from __future__ import annotations

import csv
from pathlib import Path

try:
    from scripts._route_a_scope import REPO_ROOT, load_route_a_docs
except ModuleNotFoundError:
    from _route_a_scope import REPO_ROOT, load_route_a_docs

OUTPUT = REPO_ROOT / "data" / "ledger" / "route_a_master_ledger.csv"


def main() -> None:
    docs = load_route_a_docs()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "doc_id",
        "source_filename",
        "year",
        "epoch",
        "route",
        "extract_status",
        "structured_status",
        "embedding_status",
        "metrics_status",
        "processed_present",
        "structured_present",
        "embedding_present",
        "upstream_complete",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for d in docs:
            writer.writerow(
                {
                    "doc_id": d.doc_id,
                    "source_filename": d.source_filename,
                    "year": d.year,
                    "epoch": d.epoch,
                    "route": d.route,
                    "extract_status": d.extract_status,
                    "structured_status": d.structured_status,
                    "embedding_status": d.embedding_status,
                    "metrics_status": d.metrics_status,
                    "processed_present": int(d.processed_present),
                    "structured_present": int(d.structured_present),
                    "embedding_present": int(d.embedding_present),
                    "upstream_complete": int(d.upstream_complete),
                }
            )

    years = sorted({d.year for d in docs})
    missing_years = []
    if years:
        present = set(years)
        missing_years = [y for y in range(min(years), max(years) + 1) if y not in present]

    print(f"[WROTE] {OUTPUT}")
    print(f"[TOTAL FILES] {len(docs)}")
    print(f"[TOTAL YEARS] {len(years)}")
    print(f"[MISSING YEARS] {len(missing_years)}")
    print(f"[MISSING LIST] {missing_years}")


if __name__ == "__main__":
    main()
