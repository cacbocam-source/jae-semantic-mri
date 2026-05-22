from __future__ import annotations
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "data" / "ledger" / "route_a_master_ledger.csv"
YEAR_GAP = REPO_ROOT / "analysis_outputs" / "tables" / "route_a_year_gap_2000_2026.csv"
DASHBOARD = REPO_ROOT / "analysis_outputs" / "tables" / "Route_A_Modern_progress_dashboard.csv"

INGESTION_LOG = REPO_ROOT / "docs" / "INGESTION_LOG.md"
CORPUS_COVERAGE = REPO_ROOT / "docs" / "CORPUS_COVERAGE.md"
PIPELINE_AUDIT = REPO_ROOT / "docs" / "PIPELINE_AUDIT.md"

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
    dashboard_rows = read_csv(DASHBOARD)

    dash = {r["metric"]: r["value"] for r in dashboard_rows}

    total_docs = len(ledger_rows)
    years = sorted({int(r["year"]) for r in ledger_rows if str(r.get("year", "")).strip().isdigit()})
    year_min = years[0] if years else "NA"
    year_max = years[-1] if years else "NA"

    covered = [r for r in gap_rows if (r.get("status") or "").strip().lower() == "covered"]
    missing = [r for r in gap_rows if (r.get("status") or "").strip().lower() == "missing"]

    upstream_complete = sum(as_int(r, "upstream_complete") for r in ledger_rows)
    extract_success = sum((r.get("extract_status") or "").strip().lower() == "success" for r in ledger_rows)
    structured_success = sum((r.get("structured_status") or "").strip().lower() == "success" for r in ledger_rows)
    embedding_success = sum((r.get("embedding_status") or "").strip().lower() == "success" for r in ledger_rows)
    metrics_success = sum((r.get("metrics_status") or "").strip().lower() == "success" for r in ledger_rows)

    INGESTION_LOG.write_text(
        "\n".join([
            "# Route_A Modern Ingestion Log",
            "",
            f"- Document count: {total_docs}",
            f"- Year span: {year_min}-{year_max}",
            f"- Upstream complete: {upstream_complete}",
            f"- Extract success: {extract_success}",
            f"- Structured success: {structured_success}",
            f"- Embedding success: {embedding_success}",
            f"- Metrics success: {metrics_success}",
            "",
        ]) + "\n",
        encoding="utf-8",
    )

    CORPUS_COVERAGE.write_text(
        "\n".join([
            "# Route_A Modern Corpus Coverage",
            "",
            f"- Covered years: {len(covered)}",
            f"- Missing years: {len(missing)}",
            f"- Span: {year_min}-{year_max}",
            "",
            "## Missing years",
            "",
            ", ".join(r["year"] for r in missing) if missing else "None",
            "",
        ]) + "\n",
        encoding="utf-8",
    )

    PIPELINE_AUDIT.write_text(
        "\n".join([
            "# Route_A Modern Pipeline Audit",
            "",
            "- Source of truth for Route_A scope: pipeline manifest + processed/structured/embedding artifact presence.",
            "- Raw PDF folder is no longer treated as authoritative for corpus-scope reporting.",
            "",
            f"- Dashboard total_docs: {dash.get('total_docs', 'NA')}",
            f"- Dashboard covered_years: {dash.get('covered_years', 'NA')}",
            f"- Dashboard missing_years_count: {dash.get('missing_years_count', 'NA')}",
            f"- Dashboard extract_success: {dash.get('extract_success', 'NA')}",
            f"- Dashboard structured_success: {dash.get('structured_success', 'NA')}",
            f"- Dashboard embedding_success: {dash.get('embedding_success', 'NA')}",
            f"- Dashboard metrics_success: {dash.get('metrics_success', 'NA')}",
            "",
        ]) + "\n",
        encoding="utf-8",
    )

    print(f"[WROTE] {INGESTION_LOG}")
    print(f"[WROTE] {CORPUS_COVERAGE}")
    print(f"[WROTE] {PIPELINE_AUDIT}")

if __name__ == "__main__":
    main()
