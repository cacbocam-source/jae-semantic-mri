from __future__ import annotations

from pathlib import Path

from bins.s06_analysis.loaders import (
    extract_epoch_table,
    extract_velocity_table,
    summarize_route,
    load_metrics,
)

OUTPUT_DIR = Path("analysis_outputs/summaries")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_route_report(route_name: str) -> Path:
    summary = summarize_route(route_name)
    metrics = load_metrics(route_name)
    epoch_rows = extract_epoch_table(metrics)
    velocity_rows = extract_velocity_table(metrics)

    output_path = OUTPUT_DIR / f"{route_name}_summary.md"

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


def run() -> None:
    routes = ["Route_A_Modern", "Route_B_Legacy"]

    for route_name in routes:
        try:
            path = build_route_report(route_name)
            print(f"[REPORT] {path}")
        except Exception as exc:
            print(f"[FAIL] {route_name}: {exc}")


if __name__ == "__main__":
    run()