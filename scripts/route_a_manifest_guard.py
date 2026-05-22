#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path


def load_manifest_names(manifest_path: Path, year: int) -> set[str]:
    names: set[str] = set()
    with manifest_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("route") != "Route_A_Modern":
                continue
            if str(row.get("year", "")).strip() != str(year):
                continue
            src = (row.get("source_filename") or "").strip()
            if src:
                names.add(src)
    return names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--manifest-path", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    year = args.year
    source_dir = args.source_dir.expanduser().resolve()
    manifest_path = args.manifest_path.resolve()
    raw_dir = args.raw_dir.resolve()
    output_dir = args.output_dir.resolve()

    allowed_dir = output_dir / "allowed"
    audit_dir = output_dir / "audit"
    shutil.rmtree(allowed_dir, ignore_errors=True)
    allowed_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    manifest_names = load_manifest_names(manifest_path, year)
    raw_names = {p.name for p in raw_dir.glob(f"{year}_*.pdf")}

    staged = sorted(source_dir.glob("*.pdf"))
    if not staged:
        raise FileNotFoundError(f"No PDF files found in source_dir: {source_dir}")

    rows = []
    allow_count = 0
    deny_count = 0

    for pdf in staged:
        source_name = pdf.name
        target_name = f"{year}_{source_name}"

        reasons = []
        if target_name in manifest_names:
            reasons.append("manifest_match")
        if target_name in raw_names:
            reasons.append("raw_match")

        if reasons:
            decision = "DENY"
            deny_count += 1
        else:
            decision = "ALLOW"
            allow_count += 1
            shutil.copy2(pdf, allowed_dir / source_name)

        rows.append({
            "source_name": source_name,
            "target_name": target_name,
            "decision": decision,
            "reasons": ";".join(reasons) if reasons else "novel",
        })

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audit_path = audit_dir / f"route_a_manifest_guard_{year}_{stamp}.csv"
    with audit_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source_name", "target_name", "decision", "reasons"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[GUARD] year={year}")
    print(f"[GUARD] source_dir={source_dir}")
    print(f"[GUARD] allow_count={allow_count}")
    print(f"[GUARD] deny_count={deny_count}")
    print(f"[GUARD] allowed_dir={allowed_dir}")
    print(f"[GUARD] audit_path={audit_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
