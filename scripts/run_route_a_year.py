from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bins.s01_ingest.ledger import make_doc_id

REPO_ROOT = Path("/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit")
RAW_DIR = REPO_ROOT / "data" / "raw" / "Route_A_Modern"
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "Route_A_Modern"
MANIFEST_PATH = REPO_ROOT / "data" / "manifests" / "pipeline_manifest.csv"

LEDGER_SCRIPT = REPO_ROOT / "scripts" / "build_route_a_ledger.py"
YEAR_GAP_SCRIPT = REPO_ROOT / "scripts" / "route_a_year_gap.py"
DASHBOARD_SCRIPT = REPO_ROOT / "scripts" / "build_route_a_dashboard.py"

DOCS_SCRIPT = REPO_ROOT / "scripts" / "build_route_a_docs.py"
GUARD_SCRIPT = REPO_ROOT / "scripts" / "route_a_manifest_guard.py"
GUARDED_STAGING_ROOT = REPO_ROOT / "data" / "staging" / "route_a_guard"



def run_cmd(cmd: List[str], *, use_pythonpath: bool = False) -> None:
    env = os.environ.copy()
    if use_pythonpath:
        env["PYTHONPATH"] = "."
    subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=True)


def prepare_guarded_source(year: int, source_dir: Path) -> Path:
    if not GUARD_SCRIPT.exists():
        raise FileNotFoundError(f"Guard script not found: {GUARD_SCRIPT}")

    guard_output_dir = GUARDED_STAGING_ROOT / str(year)
    allowed_dir = guard_output_dir / "allowed"

    run_cmd(
        [
            "python3",
            str(GUARD_SCRIPT),
            "--year",
            str(year),
            "--source-dir",
            str(source_dir),
            "--manifest-path",
            str(MANIFEST_PATH),
            "--raw-dir",
            str(RAW_DIR),
            "--output-dir",
            str(guard_output_dir),
        ]
    )

    allowed = sorted(allowed_dir.glob("*.pdf"))
    if not allowed:
        print(f"[GUARD] No novel Route_A_Modern PDFs remain for {year}. Exiting before migration.")
        raise SystemExit(0)

    print(f"[GUARD] allowed_count={len(allowed)}")
    print(f"[GUARD] using guarded source: {allowed_dir}")
    return allowed_dir


def import_year_pdfs(year: int, source_dir: Path) -> int:
    pdfs = sorted(source_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDF files found in source_dir: {source_dir}")

    copied = 0
    denied = 0
    for pdf in pdfs:
        dest = RAW_DIR / f"{year}_{pdf.name}"
        if dest.exists():
            print(f"[DENY] duplicate raw target exists: {dest.name}")
            denied += 1
            continue
        shutil.copy2(str(pdf), str(dest))
        copied += 1

    print(f"[IMPORT] copied={copied} denied={denied} year={year}")
    return copied


def register_year_in_manifest(year: int) -> int:
    year_prefix = f"{year}_"
    pdfs = sorted(RAW_DIR.glob(f"{year_prefix}*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No normalized PDFs found for year {year} in {RAW_DIR}")

    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        existing: List[Dict[str, str]] = list(csv.DictReader(f))

    if not existing:
        raise ValueError("Manifest is empty; cannot infer manifest fieldnames.")

    existing_ids = {row["doc_id"] for row in existing}

    new_rows: List[Dict[str, str]] = []
    for pdf in pdfs:
        abs_path = pdf.resolve()
        doc_id = make_doc_id(abs_path)
        if doc_id in existing_ids:
            continue

        new_rows.append(
            {
                "doc_id": doc_id,
                "source_pdf_path": str(abs_path),
                "source_filename": pdf.name,
                "route": "Route_A_Modern",
                "year": str(year),
                "extract_status": "pending",
                "structured_status": "pending",
                "embedding_status": "pending",
                "metrics_status": "pending",
                "extract_method": "",
                "page_count": "",
                "error_message": "",
                "last_stage_run": "",
                "artifact_version": "1.0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    if not new_rows:
        print(f"[INFO] No new manifest rows to add for {year}")
        return 0

    with MANIFEST_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=existing[0].keys())
        writer.writerows(new_rows)

    return len(new_rows)


def count_raw_pdfs(year: int) -> int:
    return len(list(RAW_DIR.glob(f"{year}_*.pdf")))


def count_manifest_rows(year: int) -> int:
    needle = f"{year}_"
    count = 0
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["route"] == "Route_A_Modern" and needle in row["source_filename"]:
                count += 1
    return count


def count_processed_txt(year: int) -> int:
    return len(list(PROCESSED_DIR.glob(f"{year}_*.txt")))


def read_year_gap_line(year: int) -> str:
    gap_path = REPO_ROOT / "analysis_outputs" / "tables" / "route_a_year_gap_2000_2026.csv"
    if not gap_path.exists():
        return "[WARN] year-gap artifact not found"

    with gap_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["year"] == str(year):
                return f"{row['year']},{row['epoch']},{row['status']}"
    return f"[WARN] year {year} not found in year-gap artifact"


def main() -> int:
    parser = argparse.ArgumentParser(description="Automate full Route_A year ingestion loop")
    parser.add_argument("--year", type=int, required=True, help="Target Route_A year, e.g. 2010")
    parser.add_argument(
        "--source-dir",
        type=Path,
        required=True,
        help="Directory containing only the target-year PDF files to import",
    )
    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Skip importing PDFs and assume normalized raw files already exist",
    )
    parser.add_argument(
        "--run-global-phases",
        action="store_true",
        help="Explicitly allow broad main.py process/analyze phases. Default is OFF for safety.",
    )
    parser.add_argument(
        "--run-corpus-rebuilds",
        action="store_true",
        help="Explicitly allow corpus-wide metrics/report/figure rebuilds. Default is OFF for safety.",
    )
    args = parser.parse_args()

    year = args.year
    source_dir = args.source_dir.expanduser().resolve()

    if not REPO_ROOT.exists():
        raise FileNotFoundError(f"Repo root not found: {REPO_ROOT}")

    if not args.skip_import:
        guarded_source_dir = prepare_guarded_source(year, source_dir)
        moved = import_year_pdfs(year, guarded_source_dir)
        if moved == 0:
            print(f"[IMPORT] No new guarded PDFs were copied for year={year}. Exiting.")
            raise SystemExit(0)
    else:
        print(f"[IMPORT] skipped year={year}")

    added = register_year_in_manifest(year)
    print(f"[MANIFEST] added={added} year={year}")

    if args.run_global_phases:
        print("[PHASE] process")
        run_cmd(["python3", "main.py", "--phase", "process"])

        print("[PHASE] analyze")
        run_cmd(["python3", "main.py", "--phase", "analyze"])
    else:
        print("[SAFE-STOP] Broad main.py process/analyze phases are disabled by default.")
        print("[SAFE-STOP] This prevents accidental full-corpus or legacy execution.")
        print("[SAFE-STOP] Use --run-global-phases only after a targeted modern-only phase runner exists.")

    print("[REBUILD] route_a ledger")
    run_cmd(["python3", str(LEDGER_SCRIPT)])

    print("[REBUILD] route_a year-gap")
    run_cmd(["python3", str(YEAR_GAP_SCRIPT)])

    print("[REBUILD] route_a dashboard")
    run_cmd(["python3", str(DASHBOARD_SCRIPT)])

    print("[REBUILD] route_a docs")
    run_cmd(["python3", str(DOCS_SCRIPT)])

    if args.run_corpus_rebuilds:
        print("[REBUILD] corpus metrics + reports + figures")
        run_cmd(["python3", "bins/s03_analysis/metrics.py"], use_pythonpath=True)
        run_cmd(["python3", "bins/s06_analysis/report_builder.py"], use_pythonpath=True)
        run_cmd(["python3", "bins/s06_analysis/apa_table_builder.py"], use_pythonpath=True)
        run_cmd(["python3", "bins/s06_analysis/figure_builder.py"], use_pythonpath=True)
        run_cmd(["python3", "bins/s06_analysis/apa_figure_builder.py"], use_pythonpath=True)
    else:
        print("[SAFE-STOP] Corpus-wide metrics/report/figure rebuilds are disabled by default.")
        print("[SAFE-STOP] This keeps Route_A_Modern intake from rebuilding global or legacy-linked artifacts.")

    raw_count = count_raw_pdfs(year)
    manifest_count = count_manifest_rows(year)
    processed_count = count_processed_txt(year)
    gap_line = read_year_gap_line(year)

    print("========================================")
    print(f"[DONE] year={year}")
    print(f"[RAW] {raw_count}")
    print(f"[MANIFEST] {manifest_count}")
    print(f"[PROCESSED] {processed_count}")
    print(f"[YEAR GAP] {gap_line}")
    print("========================================")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())