from __future__ import annotations

import csv

try:
    from scripts._route_a_scope import REPO_ROOT, load_route_a_docs, summarize_by_year
except ModuleNotFoundError:
    from _route_a_scope import REPO_ROOT, load_route_a_docs, summarize_by_year

OUTPUT = REPO_ROOT / "analysis_outputs" / "tables" / "route_a_year_gap_2000_2026.csv"


def main() -> None:
    docs = load_route_a_docs()
    rows = summarize_by_year(docs)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "year",
        "epoch",
        "status",
        "doc_count",
        "upstream_complete_count",
        "extract_success_count",
        "structured_success_count",
        "embedding_success_count",
        "metrics_success_count",
        "processed_present_count",
        "structured_present_count",
        "embedding_present_count",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    missing = [r["year"] for r in rows if r["status"] == "missing"]
    first_missing = missing[0] if missing else None

    print(f"[WROTE] {OUTPUT}")
    print(f"[MISSING YEAR] {first_missing if first_missing is not None else 0}")
    print(f"[TOTAL YEARS] {len(rows)}")
    print(f"[MISSING YEARS] {len(missing)}")
    print(f"[MISSING LIST] {missing}")


if __name__ == "__main__":
    main()
