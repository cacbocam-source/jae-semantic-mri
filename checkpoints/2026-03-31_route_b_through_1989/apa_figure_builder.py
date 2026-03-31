from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bins.s06_analysis.loaders import (
    extract_epoch_table,
    extract_velocity_table,
    load_metrics,
    summarize_route,
)


def _epoch_note_fragment(route_name: str) -> str:
    summary = summarize_route(route_name)
    labels = ", ".join(summary["epochs"])
    return f"{route_name} spans {summary['epoch_count']} validated epochs ({labels})"


def _transition_note_fragment(route_name: str) -> str:
    rows = extract_velocity_table(load_metrics(route_name))
    if not rows:
        return f"{route_name} contributes no adjacent validated epoch transitions"

    transitions = ", ".join(row["transition"] for row in rows)
    count = len(rows)
    noun = "transition" if count == 1 else "transitions"
    return f"{route_name} contributes {count} adjacent validated epoch {noun} ({transitions})"

APA_FIGURES_DIR = Path("manuscript/paper/figures")
APA_FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def build_figure_1_epoch_dispersion() -> tuple[Path, Path]:
    route_a_summary = summarize_route("Route_A_Modern")
    route_b_summary = summarize_route("Route_B_Legacy")

    route_a_rows = extract_epoch_table(load_metrics("Route_A_Modern"))
    route_b_rows = extract_epoch_table(load_metrics("Route_B_Legacy"))

    labels = []
    values = []

    for row in route_a_rows:
        labels.append(f"Modern\n{row['epoch']}")
        values.append(row["dispersion"])

    for row in route_b_rows:
        labels.append(f"Legacy\n{row['epoch']}")
        values.append(row["dispersion"])

    figure_path = APA_FIGURES_DIR / "Figure_1_epoch_dispersion.png"
    note_path = APA_FIGURES_DIR / "Figure_1_epoch_dispersion.md"

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(labels, values)
    ax.set_xlabel("Route and epoch")
    ax.set_ylabel("Semantic dispersion")
    ax.set_ylim(bottom=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    fig.tight_layout()
    fig.savefig(figure_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    note_text = "\n".join(
        [
            "**Figure 1**",
            "*Epoch-level semantic dispersion by route and epoch.*",
            "",
            (
                "Note. Bar heights report semantic dispersion for each validated route-level epoch. "
                f"In the current validated state, {_epoch_note_fragment('Route_A_Modern')}; "
                f"{_epoch_note_fragment('Route_B_Legacy')}."
            ),
            "",
        ]
    )
    note_path.write_text(note_text, encoding="utf-8")

    return figure_path, note_path


def build_figure_2_innovation_velocity() -> tuple[Path, Path]:
    velocity_rows = extract_velocity_table(load_metrics("Route_B_Legacy"))

    labels = [row["transition"] for row in velocity_rows]
    values = [row["velocity"] for row in velocity_rows]

    figure_path = APA_FIGURES_DIR / "Figure_2_innovation_velocity.png"
    note_path = APA_FIGURES_DIR / "Figure_2_innovation_velocity.md"

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(labels, values)
    ax.set_xlabel("Adjacent epoch transition")
    ax.set_ylabel("Innovation velocity")
    ax.set_ylim(bottom=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)
    ax.tick_params(axis="x", rotation=15)

    fig.tight_layout()
    fig.savefig(figure_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    note_text = "\n".join(
        [
            "**Figure 2**",
            "*Route-internal innovation velocity by adjacent validated epoch transition.*",
            "",
            (
                "Note. Innovation velocity is reported only where adjacent validated epoch transitions "
                "exist. "
                f"In the current validated state, {_transition_note_fragment('Route_A_Modern')}; "
                f"{_transition_note_fragment('Route_B_Legacy')}."
            ),
            "",
        ]
    )
    note_path.write_text(note_text, encoding="utf-8")

    return figure_path, note_path


def run() -> None:
    try:
        fig_1, note_1 = build_figure_1_epoch_dispersion()
        print(f"[APA FIGURE] {fig_1}")
        print(f"[APA NOTE]   {note_1}")
    except Exception as exc:
        print(f"[FAIL] Figure 1: {exc}")

    try:
        fig_2, note_2 = build_figure_2_innovation_velocity()
        print(f"[APA FIGURE] {fig_2}")
        print(f"[APA NOTE]   {note_2}")
    except Exception as exc:
        print(f"[FAIL] Figure 2: {exc}")


if __name__ == "__main__":
    run()