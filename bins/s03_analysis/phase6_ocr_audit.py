from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROUTE_DIR = Path("data/structured/Route_B_Legacy")
CONTROL_YEARS = range(1975, 1985)
AUDIT_YEARS = range(1985, 1995)
SECTION_KEYS = ["A_intro", "A_methods", "A_results"]
SECTION_SENTINEL = "SECTION_NOT_FOUND"
SHORT_DOCUMENT_THRESHOLD_CHARS = 200

INFERENTIAL_DIR = Path("analysis_outputs/inferential")
REPORTS_DIR = Path("analysis_outputs/reports")
FIGURES_DIR = Path("analysis_outputs/figures")

AUDIT_CSV_PATH = INFERENTIAL_DIR / "ocr_audit_1985_1994.csv"
YEAR_SUMMARY_CSV_PATH = INFERENTIAL_DIR / "ocr_audit_year_summary.csv"
REPORT_PATH = REPORTS_DIR / "ocr_audit_report.md"
FIGURE_PATH = FIGURES_DIR / "ocr_audit_figure.png"


def window_label(year: int) -> str:
    if year in CONTROL_YEARS:
        return "control_1975_1984"
    if year in AUDIT_YEARS:
        return "audit_1985_1994"
    raise ValueError(f"year {year} is outside Track A scope")


def alpha_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower())


def find_target_files() -> list[tuple[int, Path]]:
    files: list[tuple[int, Path]] = []
    for path in sorted(ROUTE_DIR.rglob("*.json")):
        match = re.search(r"/(19\d{2})/", path.as_posix())
        if not match:
            continue
        year = int(match.group(1))
        if year in CONTROL_YEARS or year in AUDIT_YEARS:
            files.append((year, path))
    return files


def safe_text(value) -> str:
    return value if isinstance(value, str) else ""


def compute_doc_metrics(year: int, path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))

    section_texts = {key: safe_text(data.get(key, "")) for key in SECTION_KEYS}
    section_not_found = {key: int(SECTION_SENTINEL in section_texts[key]) for key in SECTION_KEYS}
    section_lengths = {key: len(section_texts[key].strip()) for key in SECTION_KEYS}

    combined_parts = [
        section_texts[key].strip()
        for key in SECTION_KEYS
        if section_texts[key].strip() and SECTION_SENTINEL not in section_texts[key]
    ]
    combined_text = "\n".join(combined_parts).strip()
    combined_len = len(combined_text)

    tokens = alpha_tokens(combined_text)
    token_count = len(tokens)
    type_count = len(set(tokens))
    ttr = float(type_count / token_count) if token_count else np.nan

    non_ascii_count = sum(1 for ch in combined_text if ord(ch) > 127)
    non_ascii_rate = float(non_ascii_count / combined_len) if combined_len else np.nan

    digit_count = sum(ch.isdigit() for ch in combined_text)
    alpha_count = sum(ch.isalpha() for ch in combined_text)
    digit_alpha_ratio = float(digit_count / alpha_count) if alpha_count else np.nan

    return {
        "year": year,
        "window": window_label(year),
        "doc_id": data.get("doc_id", ""),
        "source_filename": data.get("source_filename", path.name),
        "source_pdf_path": data.get("source_pdf_path", ""),
        "source_json_path": path.as_posix(),
        "route": data.get("route", ""),
        "extraction_method": data.get("extraction_method", ""),
        "segmentation_strategy": data.get("segmentation_strategy", ""),
        "page_count": data.get("page_count", np.nan),
        "raw_text_length": data.get("raw_text_length", np.nan),
        "clean_text_length": data.get("clean_text_length", np.nan),
        "A_intro_length": section_lengths["A_intro"],
        "A_methods_length": section_lengths["A_methods"],
        "A_results_length": section_lengths["A_results"],
        "A_intro_section_not_found": section_not_found["A_intro"],
        "A_methods_section_not_found": section_not_found["A_methods"],
        "A_results_section_not_found": section_not_found["A_results"],
        "any_section_not_found": int(any(section_not_found.values())),
        "combined_text_length": combined_len,
        "short_document_flag": int(combined_len < SHORT_DOCUMENT_THRESHOLD_CHARS),
        "token_count": token_count,
        "type_count": type_count,
        "ttr": ttr,
        "non_ascii_rate": non_ascii_rate,
        "digit_alpha_ratio": digit_alpha_ratio,
    }


def build_detail_df() -> pd.DataFrame:
    rows = [compute_doc_metrics(year, path) for year, path in find_target_files()]
    if not rows:
        raise RuntimeError("No Route_B_Legacy structured JSON files found for 1975-1994")
    df = pd.DataFrame(rows)
    df = df.sort_values(["year", "source_filename"]).reset_index(drop=True)
    return df


def make_year_summary(detail_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        detail_df.groupby(["year", "window"], as_index=False)
        .agg(
            n_docs=("doc_id", "size"),
            mean_combined_text_length=("combined_text_length", "mean"),
            median_combined_text_length=("combined_text_length", "median"),
            mean_clean_text_length=("clean_text_length", "mean"),
            section_not_found_rate=("any_section_not_found", "mean"),
            short_document_rate=("short_document_flag", "mean"),
            mean_ttr=("ttr", "mean"),
            mean_non_ascii_rate=("non_ascii_rate", "mean"),
            mean_digit_alpha_ratio=("digit_alpha_ratio", "mean"),
            intro_not_found_rate=("A_intro_section_not_found", "mean"),
            methods_not_found_rate=("A_methods_section_not_found", "mean"),
            results_not_found_rate=("A_results_section_not_found", "mean"),
        )
        .sort_values("year")
        .reset_index(drop=True)
    )
    return summary


def make_window_summary(detail_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        detail_df.groupby("window", as_index=False)
        .agg(
            n_docs=("doc_id", "size"),
            mean_combined_text_length=("combined_text_length", "mean"),
            median_combined_text_length=("combined_text_length", "median"),
            mean_clean_text_length=("clean_text_length", "mean"),
            section_not_found_rate=("any_section_not_found", "mean"),
            short_document_rate=("short_document_flag", "mean"),
            mean_ttr=("ttr", "mean"),
            mean_non_ascii_rate=("non_ascii_rate", "mean"),
            mean_digit_alpha_ratio=("digit_alpha_ratio", "mean"),
            intro_not_found_rate=("A_intro_section_not_found", "mean"),
            methods_not_found_rate=("A_methods_section_not_found", "mean"),
            results_not_found_rate=("A_results_section_not_found", "mean"),
        )
        .sort_values("window")
        .reset_index(drop=True)
    )
    return summary


def fmt(value) -> str:
    if pd.isna(value):
        return "NA"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    return f"{float(value):.4f}"


def within_relative_20(audit_value: float, control_value: float) -> bool:
    if pd.isna(audit_value) or pd.isna(control_value):
        return False
    if float(control_value) == 0.0:
        return float(audit_value) == 0.0
    return abs(float(audit_value) - float(control_value)) <= 0.20 * abs(float(control_value))


def evaluate_determination(window_summary: pd.DataFrame) -> dict:
    audit = window_summary.loc[window_summary["window"] == "audit_1985_1994"].iloc[0]
    control = window_summary.loc[window_summary["window"] == "control_1975_1984"].iloc[0]

    artifact_reasons: list[str] = []

    audit_snf = float(audit["section_not_found_rate"])
    control_snf = float(control["section_not_found_rate"])
    if control_snf == 0.0:
        if audit_snf > 0.0:
            artifact_reasons.append(
                "SECTION_NOT_FOUND rate in 1985–1994 is > 0 while the control-window rate is 0.0, which satisfies the ≥2× control artifact criterion."
            )
    elif audit_snf >= 2.0 * control_snf:
        artifact_reasons.append(
            "SECTION_NOT_FOUND rate in 1985–1994 is at least 2× the control-window rate."
        )

    audit_len = float(audit["mean_combined_text_length"])
    control_len = float(control["mean_combined_text_length"])
    if control_len > 0.0 and audit_len < 0.5 * control_len:
        artifact_reasons.append(
            "Mean extraction length in 1985–1994 is below 50% of the control-window mean."
        )

    audit_non_ascii = float(audit["mean_non_ascii_rate"])
    control_non_ascii = float(control["mean_non_ascii_rate"])
    if audit_non_ascii > control_non_ascii + 0.05:
        artifact_reasons.append(
            "Non-ASCII rate in 1985–1994 exceeds the control-window rate by more than 5 percentage points."
        )

    signal_metrics = [
        "mean_combined_text_length",
        "section_not_found_rate",
        "short_document_rate",
        "mean_ttr",
        "mean_non_ascii_rate",
        "mean_digit_alpha_ratio",
    ]
    signal_checks = {
        metric: within_relative_20(float(audit[metric]), float(control[metric]))
        for metric in signal_metrics
    }
    signal_reasons = [metric for metric, ok in signal_checks.items() if ok]
    signal_flag = all(signal_checks.values())

    if artifact_reasons:
        determination = "ARTIFACT"
        rationale = "One or more explicit artifact criteria from the engineering brief were triggered."
    elif signal_flag:
        determination = "SIGNAL"
        rationale = "All audit-window metrics stayed within ±20% of the control-window values."
    else:
        determination = "INDETERMINATE"
        rationale = "No explicit artifact criterion fired, but the full metric profile also failed the all-metrics-within-±20% signal rule."

    return {
        "determination": determination,
        "rationale": rationale,
        "artifact_reasons": artifact_reasons,
        "signal_checks": signal_checks,
        "signal_reasons": signal_reasons,
    }


def write_report(detail_df: pd.DataFrame, year_summary: pd.DataFrame, window_summary: pd.DataFrame) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    audit_summary = window_summary.loc[window_summary["window"] == "audit_1985_1994"].iloc[0]
    control_summary = window_summary.loc[window_summary["window"] == "control_1975_1984"].iloc[0]
    decision = evaluate_determination(window_summary)

    worst_years = (
        year_summary.sort_values(["section_not_found_rate", "short_document_rate"], ascending=False)
        .head(5)
        [["year", "section_not_found_rate", "short_document_rate", "mean_combined_text_length"]]
    )

    lines: list[str] = []
    lines.append("# Phase 6 Track A — OCR Audit Report")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Route: Route_B_Legacy")
    lines.append("- Control window: 1975-1984")
    lines.append("- Audit window: 1985-1994")
    lines.append(f"- Documents analyzed: {len(detail_df)}")
    lines.append(f"- SECTION_NOT_FOUND sentinel: {SECTION_SENTINEL}")
    lines.append(f"- Short-document threshold: {SHORT_DOCUMENT_THRESHOLD_CHARS} characters")
    lines.append("")
    lines.append("## Window summary")
    lines.append("")
    for _, row in window_summary.iterrows():
        lines.append(
            f"- {row['window']}: n={fmt(row['n_docs'])}, "
            f"mean_combined_text_length={fmt(row['mean_combined_text_length'])}, "
            f"section_not_found_rate={fmt(row['section_not_found_rate'])}, "
            f"short_document_rate={fmt(row['short_document_rate'])}, "
            f"mean_ttr={fmt(row['mean_ttr'])}, "
            f"mean_non_ascii_rate={fmt(row['mean_non_ascii_rate'])}, "
            f"mean_digit_alpha_ratio={fmt(row['mean_digit_alpha_ratio'])}"
        )
    lines.append("")
    lines.append("## Audit-minus-control deltas")
    lines.append("")
    lines.append(
        f"- mean_combined_text_length delta = "
        f"{fmt(audit_summary['mean_combined_text_length'] - control_summary['mean_combined_text_length'])}"
    )
    lines.append(
        f"- section_not_found_rate delta = "
        f"{fmt(audit_summary['section_not_found_rate'] - control_summary['section_not_found_rate'])}"
    )
    lines.append(
        f"- short_document_rate delta = "
        f"{fmt(audit_summary['short_document_rate'] - control_summary['short_document_rate'])}"
    )
    lines.append(
        f"- mean_ttr delta = "
        f"{fmt(audit_summary['mean_ttr'] - control_summary['mean_ttr'])}"
    )
    lines.append(
        f"- mean_non_ascii_rate delta = "
        f"{fmt(audit_summary['mean_non_ascii_rate'] - control_summary['mean_non_ascii_rate'])}"
    )
    lines.append(
        f"- mean_digit_alpha_ratio delta = "
        f"{fmt(audit_summary['mean_digit_alpha_ratio'] - control_summary['mean_digit_alpha_ratio'])}"
    )
    lines.append("")
    lines.append("## Highest-risk years")
    lines.append("")
    for _, row in worst_years.iterrows():
        lines.append(
            f"- {int(row['year'])}: "
            f"section_not_found_rate={fmt(row['section_not_found_rate'])}, "
            f"short_document_rate={fmt(row['short_document_rate'])}, "
            f"mean_combined_text_length={fmt(row['mean_combined_text_length'])}"
        )
    lines.append("")
    lines.append("## Determination")
    lines.append("")
    lines.append(f"- {decision['determination']}")
    lines.append(f"- {decision['rationale']}")
    lines.append("")
    lines.append("## Rule binding")
    lines.append("")
    if decision["artifact_reasons"]:
        lines.append("- Triggered artifact criteria:")
        for reason in decision["artifact_reasons"]:
            lines.append(f"  - {reason}")
    else:
        lines.append("- No explicit artifact criterion was triggered.")
    lines.append("")
    lines.append("- ±20% signal checks:")
    for metric, ok in decision["signal_checks"].items():
        status = "PASS" if ok else "FAIL"
        lines.append(f"  - {metric}: {status}")
    lines.append("")
    lines.append("## Manuscript note")
    lines.append("")
    if decision["determination"] == "ARTIFACT":
        lines.append("- The 1985–1994 velocity anomaly should be discussed as likely contaminated by OCR/section-extraction artifact.")
        lines.append("- The epoch remains in the pipeline; this audit is diagnostic, not corrective.")
    elif decision["determination"] == "SIGNAL":
        lines.append("- The 1985–1994 velocity anomaly does not appear to be explained by OCR-quality failure under the engineering-brief thresholds.")
    else:
        lines.append("- The 1985–1994 velocity anomaly remains unresolved under the engineering-brief thresholds and should be flagged for researcher adjudication.")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


def write_figure(window_summary: pd.DataFrame) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    audit = window_summary.loc[window_summary["window"] == "audit_1985_1994"].iloc[0]
    control = window_summary.loc[window_summary["window"] == "control_1975_1984"].iloc[0]

    labels = ["SECTION_NOT_FOUND rate", "Mean extraction length"]
    audit_vals = [
        float(audit["section_not_found_rate"]),
        float(audit["mean_combined_text_length"]),
    ]
    control_vals = [
        float(control["section_not_found_rate"]),
        float(control["mean_combined_text_length"]),
    ]

    x = np.arange(len(labels))
    width = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].bar(x[:1] - width / 2, control_vals[:1], width=width, label="control_1975_1984")
    axes[0].bar(x[:1] + width / 2, audit_vals[:1], width=width, label="audit_1985_1994")
    axes[0].set_xticks(x[:1], labels[:1])
    axes[0].set_ylabel("Rate")
    axes[0].set_title("SECTION_NOT_FOUND rate")

    axes[1].bar(x[:1] - width / 2, [control_vals[1]], width=width, label="control_1975_1984")
    axes[1].bar(x[:1] + width / 2, [audit_vals[1]], width=width, label="audit_1985_1994")
    axes[1].set_xticks(x[:1], ["Mean extraction length"])
    axes[1].set_ylabel("Characters")
    axes[1].set_title("Mean extraction length")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(FIGURE_PATH, dpi=300)
    plt.close(fig)
    return FIGURE_PATH


def main() -> None:
    INFERENTIAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    detail_df = build_detail_df()
    year_summary = make_year_summary(detail_df)
    window_summary = make_window_summary(detail_df)

    audit_df = detail_df.loc[detail_df["window"] == "audit_1985_1994"].copy()

    audit_df.to_csv(AUDIT_CSV_PATH, index=False)
    print(f"[OK] csv={AUDIT_CSV_PATH}")

    year_summary.to_csv(YEAR_SUMMARY_CSV_PATH, index=False)
    print(f"[OK] csv={YEAR_SUMMARY_CSV_PATH}")

    report_path = write_report(detail_df, year_summary, window_summary)
    print(f"[OK] report={report_path}")

    figure_path = write_figure(window_summary)
    print(f"[OK] figure={figure_path}")

    decision = evaluate_determination(window_summary)
    print(f"[OK] determination={decision['determination']}")
    print("[OK] docs_analyzed=", len(detail_df))
    print("[OK] audit_docs=", len(audit_df))
    print("[OK] control_docs=", int((detail_df["window"] == "control_1975_1984").sum()))


if __name__ == "__main__":
    main()
