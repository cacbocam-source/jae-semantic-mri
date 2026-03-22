from __future__ import annotations

from bins.s06_analysis.loaders import (
    extract_epoch_table,
    extract_velocity_table,
    load_metrics,
    summarize_route,
)


def print_route_summary(route_name: str) -> None:
    summary = summarize_route(route_name)

    print(f"\n=== ROUTE SUMMARY: {route_name} ===")
    print(f"corpus_name: {summary['corpus_name']}")
    print(f"epoch_count: {summary['epoch_count']}")
    print(f"source_embedding_file_count: {summary['source_embedding_file_count']}")

    print("\nEpochs:")
    for epoch, count, dispersion in zip(
        summary["epochs"],
        summary["epoch_counts"],
        summary["semantic_dispersion"],
        strict=True,
    ):
        print(
            f"  - {epoch}: count={count}, semantic_dispersion={dispersion:.6f}"
        )

    print("\nInnovation Velocity:")
    if not summary["innovation_velocity"]:
        print("  - none (single-epoch route)")
    else:
        for idx, value in enumerate(summary["innovation_velocity"]):
            print(f"  - transition_{idx}: {value:.6f}")


def print_epoch_table(route_name: str) -> None:
    metrics = load_metrics(route_name)
    rows = extract_epoch_table(metrics)

    print(f"\n=== EPOCH TABLE: {route_name} ===")
    print("epoch | count | dispersion")
    print("-" * 40)

    for row in rows:
        print(
            f"{row['epoch']} | {row['count']} | {row['dispersion']:.6f}"
        )


def print_velocity_table(route_name: str) -> None:
    metrics = load_metrics(route_name)
    rows = extract_velocity_table(metrics)

    print(f"\n=== VELOCITY TABLE: {route_name} ===")

    if not rows:
        print("No transitions available.")
        return

    print("transition | velocity")
    print("-" * 40)

    for row in rows:
        print(f"{row['transition']} | {row['velocity']:.6f}")


def interpret_route(route_name: str) -> None:
    print_route_summary(route_name)
    print_epoch_table(route_name)
    print_velocity_table(route_name)


def run() -> None:
    routes = ["Route_A_Modern", "Route_B_Legacy"]

    for route_name in routes:
        try:
            interpret_route(route_name)
        except Exception as exc:
            print(f"[FAIL] {route_name}: {exc}")


if __name__ == "__main__":
    run()