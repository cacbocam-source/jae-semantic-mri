from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, cast

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from scipy.spatial.distance import cdist

from bins.s06_analysis.loaders import load_metrics, validate_metrics_payload

ANALYSIS_TABLES_DIR = Path("analysis_outputs/tables")
ANALYSIS_FIGURES_DIR = Path("analysis_outputs/figures")
APA_TABLES_DIR = Path("manuscript/paper/tables")
APA_FIGURES_DIR = Path("manuscript/paper/figures")

ANALYSIS_TABLES_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
APA_TABLES_DIR.mkdir(parents=True, exist_ok=True)
APA_FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def _format_plain_table(headers: list[str], rows: list[list[str]]) -> str:
    widths: list[int] = []
    for index, header in enumerate(headers):
        cell_width = max((len(row[index]) for row in rows), default=0)
        widths.append(max(len(header), cell_width))

    header_cells = [headers[index].ljust(widths[index]) for index in range(len(headers))]
    rule_cells = ["-" * widths[index] for index in range(len(headers))]
    body_lines: list[str] = []

    for row in rows:
        row_cells = [row[index].ljust(widths[index]) for index in range(len(headers))]
        body_lines.append("  ".join(row_cells))

    return "\n".join(["  ".join(header_cells), "  ".join(rule_cells), *body_lines])


def compute_bridge_row() -> dict[str, Any]:
    legacy = load_metrics("Route_B_Legacy")
    modern = load_metrics("Route_A_Modern")

    validate_metrics_payload(legacy)
    validate_metrics_payload(modern)

    legacy_labels = [str(x) for x in np.asarray(legacy["epoch_labels"]).tolist()]
    modern_labels = [str(x) for x in np.asarray(modern["epoch_labels"]).tolist()]
    legacy_centroids = np.asarray(legacy["epoch_centroids"], dtype=np.float32)
    modern_centroids = np.asarray(modern["epoch_centroids"], dtype=np.float32)
    legacy_counts = [int(x) for x in np.asarray(legacy["epoch_counts"]).tolist()]
    modern_counts = [int(x) for x in np.asarray(modern["epoch_counts"]).tolist()]

    left_epoch = legacy_labels[-1]
    right_epoch = modern_labels[0]
    left_centroid = legacy_centroids[-1].reshape(1, -1)
    right_centroid = modern_centroids[0].reshape(1, -1)

    bridge_velocity = float(cdist(left_centroid, right_centroid, metric="cosine")[0, 0])

    return {
        "left_route": "Route_B_Legacy",
        "right_route": "Route_A_Modern",
        "corpus_name": str(np.asarray(legacy["corpus_name"]).item()),
        "left_epoch": left_epoch,
        "right_epoch": right_epoch,
        "transition": f"{left_epoch} -> {right_epoch}",
        "left_n": legacy_counts[-1],
        "right_n": modern_counts[0],
        "bridge_velocity": bridge_velocity,
    }


def write_analysis_csv(row: dict[str, Any]) -> Path:
    output_path = ANALYSIS_TABLES_DIR / "bridge_transition_innovation_velocity.csv"
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "left_route",
                "right_route",
                "corpus_name",
                "left_epoch",
                "right_epoch",
                "transition",
                "left_n",
                "right_n",
                "bridge_velocity",
            ],
        )
        writer.writeheader()
        writer.writerow(row)
    return output_path


def write_apa_table(row: dict[str, Any]) -> Path:
    output_path = APA_TABLES_DIR / "Table_3_bridge_transition.md"
    rows = [[
        str(row["left_route"]),
        str(row["right_route"]),
        str(row["corpus_name"]),
        str(row["transition"]),
        str(row["left_n"]),
        str(row["right_n"]),
        f"{float(row['bridge_velocity']):.3f}",
    ]]

    content = "\n".join(
        [
            "**Table 3**",
            "*Legacy-to-Modern Bridge Innovation Velocity*",
            "",
            _format_plain_table(
                headers=[
                    "From route",
                    "To route",
                    "Corpus",
                    "Bridge transition",
                    "n (left)",
                    "n (right)",
                    "Innovation velocity",
                ],
                rows=rows,
            ),
            "",
            (
                "Note. This bridge value is the cosine distance between the Route_B_Legacy centroid "
                f"for {row['left_epoch']} and the Route_A_Modern centroid for {row['right_epoch']}. "
                "It is reported separately from route-internal innovation velocity because it crosses "
                "the legacy-to-modern route boundary."
            ),
            "",
        ]
    )
    output_path.write_text(content, encoding="utf-8")
    return output_path


def _make_bar_figure(transition: str, bridge_velocity: float) -> Figure:
    fig, ax_any = plt.subplots(figsize=(6.5, 4.5))
    ax = cast(Axes, ax_any)

    ax.bar([transition], [bridge_velocity])
    ax.set_xlabel("Bridge transition")
    ax.set_ylabel("Innovation velocity")
    ax.set_ylim(bottom=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)
    ax.tick_params(axis="x", rotation=15)

    fig.tight_layout()
    return cast(Figure, fig)


def write_analysis_figure(row: dict[str, Any]) -> Path:
    output_path = ANALYSIS_FIGURES_DIR / "bridge_transition_innovation_velocity.png"
    fig = _make_bar_figure(str(row["transition"]), float(row["bridge_velocity"]))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def write_apa_figure_and_note(row: dict[str, Any]) -> tuple[Path, Path]:
    figure_path = APA_FIGURES_DIR / "Figure_3_bridge_transition.png"
    note_path = APA_FIGURES_DIR / "Figure_3_bridge_transition.md"

    fig = _make_bar_figure(str(row["transition"]), float(row["bridge_velocity"]))
    fig.savefig(figure_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    note_text = "\n".join(
        [
            "**Figure 3**",
            "*Legacy-to-modern bridge innovation velocity.*",
            "",
            (
                "Note. The bridge value is computed as the cosine distance between the "
                f"Route_B_Legacy centroid for {row['left_epoch']} and the Route_A_Modern centroid "
                f"for {row['right_epoch']}. In the current validated state, the bridge transition "
                f"{row['transition']} has innovation velocity {float(row['bridge_velocity']):.3f}."
            ),
            "",
        ]
    )
    note_path.write_text(note_text, encoding="utf-8")
    return figure_path, note_path


def run() -> None:
    row = compute_bridge_row()

    csv_path = write_analysis_csv(row)
    print(f"[BRIDGE TABLE] {csv_path}")

    table_path = write_apa_table(row)
    print(f"[APA TABLE] {table_path}")

    fig_path = write_analysis_figure(row)
    print(f"[BRIDGE FIGURE] {fig_path}")

    apa_fig_path, note_path = write_apa_figure_and_note(row)
    print(f"[APA FIGURE] {apa_fig_path}")
    print(f"[APA NOTE]   {note_path}")


if __name__ == "__main__":
    run()
