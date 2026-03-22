from __future__ import annotations

import argparse
import shutil
from dataclasses import replace
from pathlib import Path

from jae_legacy_acquisition_contract import (
    PROJECT_ROOT_DEFAULT,
    PROMOTION_APPROVED,
    PROMOTION_PROMOTED,
    PrefillRecord,
    ensure_project_root,
    read_prefill_csv,
    resolve_under_project_root,
    write_prefill_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Promote approved staged PDFs into the canonical raw_pdfs route/year corpus."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--csv-path", type=Path, required=True)
    parser.add_argument("--move", action="store_true", help="Move instead of copy.")
    parser.add_argument(
        "--promote-all-downloaded",
        action="store_true",
        help="Promote all downloaded rows, not just promotion_status=approved.",
    )
    return parser


def should_promote(record: PrefillRecord, promote_all_downloaded: bool) -> bool:
    if not record.staged_pdf_path.strip():
        return False
    if promote_all_downloaded:
        return record.download_status == "downloaded" and record.promotion_status != PROMOTION_PROMOTED
    return record.download_status == "downloaded" and record.promotion_status == PROMOTION_APPROVED


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project_root = ensure_project_root(args.project_root)
    csv_path = args.csv_path.resolve()
    records = read_prefill_csv(csv_path)

    updated: list[PrefillRecord] = []
    for record in records:
        mutable = replace(record)
        if not should_promote(record, args.promote_all_downloaded):
            updated.append(mutable)
            continue

        source_path = resolve_under_project_root(project_root, record.staged_pdf_path)
        target_path = resolve_under_project_root(project_root, record.canonical_pdf_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if args.move:
            shutil.move(str(source_path), str(target_path))
        else:
            shutil.copy2(source_path, target_path)

        mutable.canonical_pdf_path = str(target_path)
        mutable.promotion_status = PROMOTION_PROMOTED
        print(f"[PROMOTED] {record.record_id} -> {target_path}")
        updated.append(mutable)

    write_prefill_csv(updated, csv_path)
    print(f"Updated CSV: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
