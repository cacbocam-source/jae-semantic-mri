from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

EXPORT_ROOT = Path("analysis_outputs/export_packages/full_corpus_spss")
MANIFEST_PATH = EXPORT_ROOT / "full_corpus_article_level_manifest.csv"
EPOCH_PATH = EXPORT_ROOT / "full_corpus_epoch_level_metrics.csv"
ROUTE_SUMMARY_PATH = EXPORT_ROOT / "full_corpus_route_summaries.csv"
PHASE6_PATH = EXPORT_ROOT / "full_corpus_phase6_results.csv"
PACKAGE_INDEX_PATH = EXPORT_ROOT / "package_index.csv"
OUTPUT_PATH = EXPORT_ROOT / "full_corpus_flat_analyst_file.csv"


def require_file(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def parse_year_from_row(row: pd.Series) -> float:
    for key in ["year", "source_filename", "source_pdf_path", "doc_id"]:
        value = row.get(key, "")
        if pd.isna(value):
            continue
        text = str(value)
        if key == "year":
            try:
                return float(int(float(text)))
            except Exception:
                pass
        match = re.search(r"(19|20)\d{2}", text)
        if match:
            return float(int(match.group(0)))
    return np.nan


def parse_epoch_bounds(epoch_label: str) -> tuple[float, float]:
    match = re.match(r"^\s*(\d{4})-(\d{4})\s*$", str(epoch_label))
    if not match:
        return (np.nan, np.nan)
    return (float(match.group(1)), float(match.group(2)))


def assign_epoch_label(article_year: float, route_name: str, epoch_lookup: pd.DataFrame) -> str:
    if pd.isna(article_year) or not route_name:
        return ""
    subset = epoch_lookup.loc[epoch_lookup["route_name"] == route_name]
    for _, row in subset.iterrows():
        start = row["epoch_start_year"]
        end = row["epoch_end_year"]
        if pd.notna(start) and pd.notna(end) and start <= article_year <= end:
            return str(row["epoch"])
    return ""


def build_track_b_route_summary(phase6: pd.DataFrame) -> pd.DataFrame:
    if phase6.empty or "result_family" not in phase6.columns:
        return pd.DataFrame(columns=["route_name"])

    pett = phase6.loc[phase6["result_family"] == "pett_breakpoints"].copy()
    if pett.empty:
        return pd.DataFrame(columns=["route_name"])

    keep_cols = [
        "route_name",
        "analysis",
        "left_epoch",
        "right_epoch",
        "break_index",
        "effect_size_mean_diff",
        "p_value",
        "ci_low",
        "ci_high",
    ]
    keep_cols = [c for c in keep_cols if c in pett.columns]
    pett = pett[keep_cols]

    wide_frames = []
    for analysis_name, prefix in [
        ("primary_breakpoint", "track_b_primary"),
        ("sensitivity_best_break", "track_b_sensitivity"),
    ]:
        sub = pett.loc[pett["analysis"] == analysis_name].copy()
        if sub.empty:
            continue
        sub = sub.drop(columns=["analysis"], errors="ignore")
        rename_map = {
            c: f"{prefix}_{c}"
            for c in sub.columns
            if c != "route_name"
        }
        sub = sub.rename(columns=rename_map)
        wide_frames.append(sub)

    if not wide_frames:
        return pd.DataFrame(columns=["route_name"])

    out = wide_frames[0]
    for frame in wide_frames[1:]:
        out = out.merge(frame, on="route_name", how="outer")
    return out


def build_track_a_year_summary(phase6: pd.DataFrame) -> pd.DataFrame:
    if phase6.empty or "result_family" not in phase6.columns:
        return pd.DataFrame(columns=["article_year"])

    ocr = phase6.loc[phase6["result_family"] == "ocr_audit_year_summary"].copy()
    if ocr.empty:
        return pd.DataFrame(columns=["article_year"])

    if "year" not in ocr.columns:
        return pd.DataFrame(columns=["article_year"])

    ocr["article_year"] = pd.to_numeric(ocr["year"], errors="coerce")
    drop_cols = {"phase6_track", "result_family", "year"}
    rename_map = {
        c: f"track_a_{c}"
        for c in ocr.columns
        if c not in drop_cols and c != "article_year"
    }
    ocr = ocr.rename(columns=rename_map)
    keep_cols = ["article_year"] + [c for c in ocr.columns if c.startswith("track_a_")]
    return ocr[keep_cols]


def main() -> None:
    require_file(MANIFEST_PATH)
    require_file(EPOCH_PATH)
    require_file(ROUTE_SUMMARY_PATH)

    manifest = pd.read_csv(MANIFEST_PATH)
    epoch_df = pd.read_csv(EPOCH_PATH)
    route_summary = pd.read_csv(ROUTE_SUMMARY_PATH)
    phase6 = pd.read_csv(PHASE6_PATH) if PHASE6_PATH.exists() else pd.DataFrame()

    manifest["route_name"] = manifest["route"] if "route" in manifest.columns else manifest.get("route_name", "")
    manifest["article_year"] = manifest.apply(parse_year_from_row, axis=1)

    epoch_df["route_name"] = epoch_df["route_name"].astype(str)
    epoch_df["epoch_start_year"], epoch_df["epoch_end_year"] = zip(*epoch_df["epoch"].map(parse_epoch_bounds))
    manifest["epoch"] = manifest.apply(
        lambda row: assign_epoch_label(row["article_year"], str(row["route_name"]), epoch_df),
        axis=1,
    )

    epoch_merge = epoch_df.copy()
    epoch_prefix_cols = {}
    for col in epoch_merge.columns:
        if col not in {"route_name", "epoch"}:
            epoch_prefix_cols[col] = f"epoch_{col}"
    epoch_merge = epoch_merge.rename(columns=epoch_prefix_cols)

    flat = manifest.merge(epoch_merge, on=["route_name", "epoch"], how="left")

    if "route_name" not in route_summary.columns and "route" in route_summary.columns:
        route_summary["route_name"] = route_summary["route"]

    route_prefix_cols = {}
    for col in route_summary.columns:
        if col != "route_name":
            route_prefix_cols[col] = f"route_summary_{col}"
    route_summary = route_summary.rename(columns=route_prefix_cols)

    flat = flat.merge(route_summary, on="route_name", how="left")

    track_b_summary = build_track_b_route_summary(phase6)
    if not track_b_summary.empty:
        flat = flat.merge(track_b_summary, on="route_name", how="left")

    track_a_year = build_track_a_year_summary(phase6)
    if not track_a_year.empty:
        flat = flat.merge(track_a_year, on="article_year", how="left")

    flat["route_family"] = flat["route_name"].map(
        {
            "Route_A_Modern": "modern",
            "Route_B_Legacy": "legacy",
        }
    ).fillna("unknown")
    flat["bridge_transition_reference_flag"] = 0
    flat["phase6_track_a_window_flag"] = (
        (flat["route_name"] == "Route_B_Legacy")
        & (flat["article_year"] >= 1985)
        & (flat["article_year"] <= 1994)
    ).astype(int)
    flat["phase6_track_a_determination"] = np.where(
        flat["phase6_track_a_window_flag"] == 1,
        "ARTIFACT",
        "",
    )
    flat["phase6_track_b_results_available"] = flat["route_name"].isin(
        ["Route_A_Modern", "Route_B_Legacy"]
    ).astype(int)

    flat["epoch_terminal_canonical_flag"] = (
        (flat["route_name"] == "Route_A_Modern") & (flat["epoch"] == "2025-2029")
    ).astype(int)
    flat["epoch_terminal_policy_label"] = np.where(
        flat["epoch_terminal_canonical_flag"] == 1,
        "canonical_final_terminal_epoch",
        "",
    )
    flat["epoch_terminal_policy_note"] = np.where(
        flat["epoch_terminal_canonical_flag"] == 1,
        "Route_A_Modern 2025-2029 is a known terminal epoch with 157 articles; treat as canonical and final by project policy.",
        "",
    )

    flat["flat_export_version"] = "2026-04-05_r2"

    preferred_front = [
        "doc_id",
        "route_name",
        "route_family",
        "article_year",
        "epoch",
        "source_filename",
        "source_pdf_path",
        "structured_status",
        "embedding_status",
        "metrics_status",
        "epoch_terminal_canonical_flag",
        "epoch_terminal_policy_label",
        "epoch_terminal_policy_note",
        "phase6_track_a_window_flag",
        "phase6_track_a_determination",
        "bridge_transition_reference_flag",
        "phase6_track_b_results_available",
        "track_b_primary_left_epoch",
        "track_b_primary_right_epoch",
        "track_b_primary_effect_size_mean_diff",
        "track_b_primary_p_value",
        "track_b_primary_ci_low",
        "track_b_primary_ci_high",
        "track_b_sensitivity_left_epoch",
        "track_b_sensitivity_right_epoch",
        "track_b_sensitivity_effect_size_mean_diff",
        "track_b_sensitivity_p_value",
        "track_b_sensitivity_ci_low",
        "track_b_sensitivity_ci_high",
    ]
    existing_front = [c for c in preferred_front if c in flat.columns]
    remaining = [c for c in flat.columns if c not in existing_front]
    flat = flat[existing_front + remaining]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    flat.to_csv(OUTPUT_PATH, index=False)

    if PACKAGE_INDEX_PATH.exists():
        package_index = pd.read_csv(PACKAGE_INDEX_PATH)
    else:
        package_index = pd.DataFrame(columns=["dataset_name", "path", "row_count", "description"])

    package_index = package_index.loc[
        package_index["dataset_name"] != "full_corpus_flat_analyst_file"
    ].copy()

    package_index = pd.concat(
        [
            package_index,
            pd.DataFrame(
                [
                    {
                        "dataset_name": "full_corpus_flat_analyst_file",
                        "path": str(OUTPUT_PATH),
                        "row_count": len(flat),
                        "description": "One-row-per-article SPSS-ready flat analyst file merging manifest, epoch metrics, route summaries, and Phase 6 flags/results.",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    package_index.to_csv(PACKAGE_INDEX_PATH, index=False)

    print(f"[OK] {OUTPUT_PATH}")
    print(f"[OK] row_count={len(flat)}")
    print(f"[OK] column_count={len(flat.columns)}")
    print(f"[OK] {PACKAGE_INDEX_PATH}")
    print("[COLUMNS_HEAD]")
    for name in flat.columns[:40]:
        print(name)


if __name__ == "__main__":
    main()
