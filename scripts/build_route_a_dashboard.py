from __future__ import annotations
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "data" / "ledger" / "route_a_master_ledger.csv"
YEAR_GAP = REPO_ROOT / "analysis_outputs" / "tables" / "route_a_year_gap_2000_2026.csv"
OUT_CSV = REPO_ROOT / "analysis_outputs" / "tables" / "Route_A_Modern_progress_dashboard.csv"
OUT_MD = REPO_ROOT / "analysis_outputs" / "summaries" / "Route_A_Modern_progress_dashboard.md"

def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def as_int(row: dict, key: str) -> int:
    try:
        return int(str(row.get(key, 0)).strip() or 0)
    except Exception:
        return 0

def main() -> None:
    ledger_rows = read_csv(LEDGER)
    gap_rows = read_csv(YEAR_GAP)

    total_docs = len(ledger_rows)
    total_years = len(gap_rows)
    covered_years = sum((r.get("status") or "").strip().lower() == "covered" for r in gap_rows)
    missing_years = [r["year"] for r in gap_rows if (r.get("status") or "").strip().lower() == "missing"]

    upstream_complete = sum(as_int(r, "upstream_complete") for r in ledger_rows)
    extract_success = sum((r.get("extract_status") or "").strip().lower() == "success" for r in ledger_rows)
    structured_success = sum((r.get("structured_status") or "").strip().lower() == "success" for r in ledger_rows)
    embedding_success = sum((r.get("embedding_status") or "").strip().lower() == "success" for r in ledger_rows)
    metrics_success = sum((r.get("metrics_status") or "").strip().lower() == "success" for r in ledger_rows)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    dashboard_rows = [
        {"metric": "route", "value": "Route_A_Modern"},
        {"metric": "total_docs", "value": total_docs},
        {"metric": "total_years", "value": total_years},
        {"metric": "covered_years", "value": covered_years},
        {"metric": "missing_years_count", "value": len(missing_years)},
        {"metric": "missing_years", "value": ",".join(str(y) for y in missing_years)},
        {"metric": "extract_success", "value": extract_success},
        {"metric": "structured_success", "value": structured_success},
        {"metric": "embedding_success", "value": embedding_success},
        {"metric": "metrics_success", "value": metrics_success},
        {"metric": "upstream_complete", "value": upstream_complete},
    ]

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(dashboard_rows)

    md = []
    md.append("# Route_A_Modern Progress Dashboard")
    md.append("")
    md.append(f"- Total documents: {total_docs}")
    md.append(f"- Total years in span: {total_years}")
    md.append(f"- Covered years: {covered_years}")
    md.append(f"- Missing years: {len(missing_years)}")
    md.append(f"- Extract success: {extract_success}")
    md.append(f"- Structured success: {structured_success}")
    md.append(f"- Embedding success: {embedding_success}")
    md.append(f"- Metrics success: {metrics_success}")
    md.append(f"- Upstream complete: {upstream_complete}")
    md.append("")
    md.append("## Missing years")
    md.append("")
    md.append(", ".join(str(y) for y in missing_years) if missing_years else "None")

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[WROTE] {OUT_CSV}")
    print(f"[WROTE] {OUT_MD}")

if __name__ == "__main__":
    main()
