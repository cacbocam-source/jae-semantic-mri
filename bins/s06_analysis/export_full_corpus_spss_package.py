from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

import pandas as pd

from bins.s06_analysis.loaders import (
    extract_epoch_table,
    extract_velocity_table,
    load_metrics,
    summarize_route,
    validate_metrics_payload,
)

ROOT = Path(".")
MANIFEST_PATH = ROOT / "data/manifests/pipeline_manifest.csv"
TABLES_DIR = ROOT / "analysis_outputs/tables"
INFERENTIAL_DIR = ROOT / "analysis_outputs/inferential"
REPORTS_DIR = ROOT / "analysis_outputs/reports"
FIGURES_DIR = ROOT / "analysis_outputs/figures"

EXPORT_ROOT = ROOT / "analysis_outputs/export_packages/full_corpus_spss"
EXPORT_FIGURES = EXPORT_ROOT / "figures"

ROUTES = ["Route_A_Modern", "Route_B_Legacy"]


def ensure_dirs() -> None:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    EXPORT_FIGURES.mkdir(parents=True, exist_ok=True)


def maybe_read_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def add_manifest_derivations(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = pd.to_numeric(out.get("year"), errors="coerce")
    out["route_family"] = out.get("route", "").map(
        {
            "Route_A_Modern": "modern",
            "Route_B_Legacy": "legacy",
        }
    ).fillna("unknown")
    out["is_modern"] = (out["route"] == "Route_A_Modern").astype(int)
    out["is_legacy"] = (out["route"] == "Route_B_Legacy").astype(int)
    out["all_core_status_success"] = (
        (out.get("structured_status", "") == "success")
        & (out.get("embedding_status", "") == "success")
        & (out.get("metrics_status", "") == "success")
    ).astype(int)
    out["export_source"] = "pipeline_manifest"
    return out


def route_epoch_df(route_name: str) -> pd.DataFrame:
    metrics = load_metrics(route_name)
    validate_metrics_payload(metrics)
    rows = extract_epoch_table(metrics)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["route_name"] = route_name
    df["analysis_family"] = "core_epoch_metrics"
    return df


def route_velocity_df(route_name: str) -> pd.DataFrame:
    metrics = load_metrics(route_name)
    validate_metrics_payload(metrics)
    rows = extract_velocity_table(metrics)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["route_name"] = route_name
    df["analysis_family"] = "core_velocity_metrics"
    return df


def route_summary_df(route_name: str) -> pd.DataFrame:
    summary = summarize_route(route_name)
    df = pd.DataFrame([summary])
    df["route_name"] = route_name
    df["analysis_family"] = "route_summary"
    return df


def combine_phase6_results() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    pett_breaks = maybe_read_csv(INFERENTIAL_DIR / "phase6_pett_breakpoints.csv")
    if not pett_breaks.empty:
        pett_breaks["phase6_track"] = "Track_B"
        pett_breaks["result_family"] = "pett_breakpoints"
        frames.append(pett_breaks)

    pett_secondary = maybe_read_csv(INFERENTIAL_DIR / "phase6_pett_secondary_tests.csv")
    if not pett_secondary.empty:
        pett_secondary["phase6_track"] = "Track_B"
        pett_secondary["result_family"] = "pett_secondary_tests"
        frames.append(pett_secondary)

    ocr_year = maybe_read_csv(INFERENTIAL_DIR / "ocr_audit_year_summary.csv")
    if not ocr_year.empty:
        ocr_year["phase6_track"] = "Track_A"
        ocr_year["result_family"] = "ocr_audit_year_summary"
        frames.append(ocr_year)

    ocr_doc = maybe_read_csv(INFERENTIAL_DIR / "ocr_audit_1985_1994.csv")
    if not ocr_doc.empty:
        ocr_doc["phase6_track"] = "Track_A"
        ocr_doc["result_family"] = "ocr_audit_doc_level_1985_1994"
        frames.append(ocr_doc)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True, sort=False)


def copy_if_exists(src: Path, dst: Path) -> bool:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def export_package() -> None:
    ensure_dirs()

    manifest = pd.read_csv(MANIFEST_PATH)
    manifest = add_manifest_derivations(manifest)
    manifest_out = EXPORT_ROOT / "full_corpus_article_level_manifest.csv"
    manifest.to_csv(manifest_out, index=False)

    epoch_frames = [route_epoch_df(route) for route in ROUTES]
    epoch_df = pd.concat(epoch_frames, ignore_index=True, sort=False)
    epoch_out = EXPORT_ROOT / "full_corpus_epoch_level_metrics.csv"
    epoch_df.to_csv(epoch_out, index=False)

    velocity_frames = [route_velocity_df(route) for route in ROUTES]
    velocity_df = pd.concat(velocity_frames, ignore_index=True, sort=False)
    velocity_out = EXPORT_ROOT / "full_corpus_velocity_level_metrics.csv"
    velocity_df.to_csv(velocity_out, index=False)

    summary_frames = [route_summary_df(route) for route in ROUTES]
    summary_df = pd.concat(summary_frames, ignore_index=True, sort=False)
    summary_out = EXPORT_ROOT / "full_corpus_route_summaries.csv"
    summary_df.to_csv(summary_out, index=False)

    bridge_src = TABLES_DIR / "bridge_transition_innovation_velocity.csv"
    bridge_out = EXPORT_ROOT / "full_corpus_bridge_transition.csv"
    bridge_exists = copy_if_exists(bridge_src, bridge_out)

    phase6_df = combine_phase6_results()
    phase6_out = EXPORT_ROOT / "full_corpus_phase6_results.csv"
    if not phase6_df.empty:
        phase6_df.to_csv(phase6_out, index=False)

    copied_figures: list[str] = []
    for fig_name in [
        "Route_A_Modern_epoch_dispersion.png",
        "Route_B_Legacy_epoch_dispersion.png",
        "Route_A_Modern_innovation_velocity.png",
        "Route_B_Legacy_innovation_velocity.png",
        "Route_A_Modern_phase6_pett_dispersion.png",
        "Route_B_Legacy_phase6_pett_dispersion.png",
        "ocr_audit_figure.png",
    ]:
        src = FIGURES_DIR / fig_name
        if copy_if_exists(src, EXPORT_FIGURES / fig_name):
            copied_figures.append(fig_name)

    package_index_rows = [
        {
            "dataset_name": "full_corpus_article_level_manifest",
            "path": str(manifest_out),
            "row_count": len(manifest),
            "description": "Full-corpus article-level manifest with route/status derivations for SPSS.",
        },
        {
            "dataset_name": "full_corpus_epoch_level_metrics",
            "path": str(epoch_out),
            "row_count": len(epoch_df),
            "description": "Unified epoch-level core semantic metrics across Route_A_Modern and Route_B_Legacy.",
        },
        {
            "dataset_name": "full_corpus_velocity_level_metrics",
            "path": str(velocity_out),
            "row_count": len(velocity_df),
            "description": "Unified innovation-velocity records across Route_A_Modern and Route_B_Legacy.",
        },
        {
            "dataset_name": "full_corpus_route_summaries",
            "path": str(summary_out),
            "row_count": len(summary_df),
            "description": "Route-level summaries from the loaders/report layer.",
        },
        {
            "dataset_name": "full_corpus_bridge_transition",
            "path": str(bridge_out),
            "row_count": len(pd.read_csv(bridge_out)) if bridge_exists else 0,
            "description": "Bridge transition table copied from analysis_outputs/tables if present.",
        },
        {
            "dataset_name": "full_corpus_phase6_results",
            "path": str(phase6_out),
            "row_count": len(phase6_df),
            "description": "Unified Phase 6 Track A + Track B inferential outputs.",
        },
    ]
    package_index = pd.DataFrame(package_index_rows)
    package_index_out = EXPORT_ROOT / "package_index.csv"
    package_index.to_csv(package_index_out, index=False)

    readme = EXPORT_ROOT / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Full Corpus SPSS Export Package",
                "",
                "This package consolidates the core semantic metrics layer, interpretation/report layer, bridge table, and Phase 6 inferential outputs into SPSS-ready CSVs.",
                "",
                "Primary files:",
                "- full_corpus_article_level_manifest.csv",
                "- full_corpus_epoch_level_metrics.csv",
                "- full_corpus_velocity_level_metrics.csv",
                "- full_corpus_route_summaries.csv",
                "- full_corpus_bridge_transition.csv",
                "- full_corpus_phase6_results.csv",
                "- package_index.csv",
                "",
                "Figures are copied into ./figures for reference.",
            ]
        ),
        encoding="utf-8",
    )

    print(f"[OK] {manifest_out}")
    print(f"[OK] {epoch_out}")
    print(f"[OK] {velocity_out}")
    print(f"[OK] {summary_out}")
    if bridge_exists:
        print(f"[OK] {bridge_out}")
    else:
        print(f"[WARN] missing bridge source table: {bridge_src}")
    if not phase6_df.empty:
        print(f"[OK] {phase6_out}")
    else:
        print("[WARN] no Phase 6 result CSVs found to combine")
    print(f"[OK] {package_index_out}")
    print(f"[OK] {readme}")
    print(f"[OK] copied_figures={len(copied_figures)}")
    for fig_name in copied_figures:
        print(f"[FIG] {fig_name}")


if __name__ == "__main__":
    export_package()
