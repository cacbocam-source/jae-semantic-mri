from __future__ import annotations

import csv
from pathlib import Path

from bins.s06_analysis.loaders import (
    extract_epoch_table,
    extract_velocity_table,
    summarize_route,
    load_metrics,
)

SUMMARYS_DIR = Path("analysis_outputs/summaries")
TABLES_DIR = Path("analysis_outputs/tables")
SUMMARYS_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def _write_csv(output_path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def build_epoch_table_export(route_name: str) -> Path:
    summary = summarize_route(route_name)
    metrics = load_metrics(route_name)
    epoch_rows = extract_epoch_table(metrics)

    output_path = TABLES_DIR / f"{route_name}_epoch_summary.csv"
    export_rows = [
        {
            "route_name": summary["route_name"],
            "corpus_name": summary["corpus_name"],
            "epoch": row["epoch"],
            "count": row["count"],
            "semantic_dispersion": row["dispersion"],
        }
        for row in epoch_rows
    ]

    return _write_csv(
        output_path=output_path,
        fieldnames=[
            "route_name",
            "corpus_name",
            "epoch",
            "count",
            "semantic_dispersion",
        ],
        rows=export_rows,
    )


def build_velocity_table_export(route_name: str) -> Path:
    summary = summarize_route(route_name)
    metrics = load_metrics(route_name)
    velocity_rows = extract_velocity_table(metrics)

    output_path = TABLES_DIR / f"{route_name}_innovation_velocity.csv"
    export_rows = [
        {
            "route_name": summary["route_name"],
            "corpus_name": summary["corpus_name"],
            "transition": row["transition"],
            "velocity": row["velocity"],
        }
        for row in velocity_rows
    ]

    return _write_csv(
        output_path=output_path,
        fieldnames=[
            "route_name",
            "corpus_name",
            "transition",
            "velocity",
        ],
        rows=export_rows,
    )


def build_route_report(route_name: str) -> Path:
    summary = summarize_route(route_name)
    metrics = load_metrics(route_name)
    epoch_rows = extract_epoch_table(metrics)
    velocity_rows = extract_velocity_table(metrics)

    output_path = SUMMARYS_DIR / f"{route_name}_summary.md"

    with output_path.open("w", encoding="utf-8") as f:
        f.write(f"# Route Summary: {route_name}\n\n")

        f.write("## Overview\n\n")
        f.write(f"- Corpus: {summary['corpus_name']}\n")
        f.write(f"- Route: {summary['route_name']}\n")
        f.write(f"- Epoch count: {summary['epoch_count']}\n")
        f.write(f"- Source embedding files: {summary['source_embedding_file_count']}\n\n")

        f.write("## Epoch Summary\n\n")
        f.write("| Epoch | Count | Semantic Dispersion |\n")
        f.write("|------|------:|--------------------:|\n")
        for row in epoch_rows:
            f.write(
                f"| {row['epoch']} | {row['count']} | {row['dispersion']:.6f} |\n"
            )

        f.write("\n## Innovation Velocity\n\n")
        if not velocity_rows:
            f.write("No transitions available.\n")
        else:
            f.write("| Transition | Velocity |\n")
            f.write("|-----------|---------:|\n")
            for row in velocity_rows:
                f.write(f"| {row['transition']} | {row['velocity']:.6f} |\n")

    return output_path


def build_route_artifacts(route_name: str) -> dict[str, Path]:
    return {
        "summary": build_route_report(route_name),
        "epoch_table": build_epoch_table_export(route_name),
        "velocity_table": build_velocity_table_export(route_name),
    }


def run() -> None:
    routes = ["Route_A_Modern", "Route_B_Legacy"]

    for route_name in routes:
        try:
            paths = build_route_artifacts(route_name)
            print(f"[REPORT] {paths['summary']}")
            print(f"[TABLE] {paths['epoch_table']}")
            print(f"[TABLE] {paths['velocity_table']}")
        except Exception as exc:
            print(f"[FAIL] {route_name}: {exc}")


if __name__ == "__main__":
    run()