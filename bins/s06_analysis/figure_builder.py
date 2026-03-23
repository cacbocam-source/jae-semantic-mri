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

FIGURES_DIR = Path("analysis_outputs/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(name: str) -> str:
    return name.replace(" ", "_").replace("/", "_")


def build_epoch_dispersion_figure(route_name: str) -> Path:
    summary = summarize_route(route_name)
    metrics = load_metrics(route_name)
    rows = extract_epoch_table(metrics)

    epochs = [row["epoch"] for row in rows]
    dispersion = [row["dispersion"] for row in rows]

    output_path = FIGURES_DIR / f"{_sanitize_filename(route_name)}_epoch_dispersion.png"

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(epochs, dispersion)
    ax.set_title(f"{route_name} — Semantic Dispersion by Epoch")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Semantic Dispersion")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.3)

    corpus_name = summary["corpus_name"]
    fig.text(0.01, 0.01, f"Corpus: {corpus_name}", fontsize=9)

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return output_path


def build_innovation_velocity_figure(route_name: str) -> Path | None:
    summary = summarize_route(route_name)
    metrics = load_metrics(route_name)
    rows = extract_velocity_table(metrics)

    if not rows:
        return None

    transitions = [row["transition"] for row in rows]
    velocity = [row["velocity"] for row in rows]

    output_path = FIGURES_DIR / f"{_sanitize_filename(route_name)}_innovation_velocity.png"

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(transitions, velocity)
    ax.set_title(f"{route_name} — Innovation Velocity by Transition")
    ax.set_xlabel("Transition")
    ax.set_ylabel("Innovation Velocity")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(axis="x", rotation=20)

    corpus_name = summary["corpus_name"]
    fig.text(0.01, 0.01, f"Corpus: {corpus_name}", fontsize=9)

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return output_path


def build_route_figures(route_name: str) -> dict[str, Path | None]:
    return {
        "epoch_dispersion": build_epoch_dispersion_figure(route_name),
        "innovation_velocity": build_innovation_velocity_figure(route_name),
    }


def run() -> None:
    routes = ["Route_A_Modern", "Route_B_Legacy"]

    for route_name in routes:
        try:
            paths = build_route_figures(route_name)
            print(f"[FIGURE] {paths['epoch_dispersion']}")

            if paths["innovation_velocity"] is None:
                print(f"[SKIP] {route_name}: no innovation-velocity transitions available")
            else:
                print(f"[FIGURE] {paths['innovation_velocity']}")
        except Exception as exc:
            print(f"[FAIL] {route_name}: {exc}")


if __name__ == "__main__":
    run()