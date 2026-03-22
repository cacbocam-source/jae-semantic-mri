from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


METRICS_DIR = Path("data/metrics")


def load_metrics(route_name: str) -> dict[str, Any]:
    path = METRICS_DIR / route_name / "metrics.npz"

    if not path.exists():
        raise FileNotFoundError(f"Metrics file not found: {path}")

    with np.load(path, allow_pickle=True) as data:
        payload: dict[str, Any] = {}
        for key in data.files:
            payload[str(key)] = data[key]
        return payload


def validate_metrics_payload(metrics: dict[str, Any]) -> None:
    required_keys = {
        "corpus_name",
        "route_name",
        "epoch_labels",
        "epoch_counts",
        "epoch_centroids",
        "semantic_dispersion",
        "innovation_velocity",
        "source_embedding_files",
        "created_at_utc",
        "metric_version",
    }

    missing = required_keys - set(metrics.keys())
    if missing:
        raise ValueError(f"Metrics payload missing required keys: {sorted(missing)}")

    epoch_labels = np.asarray(metrics["epoch_labels"])
    epoch_counts = np.asarray(metrics["epoch_counts"])
    epoch_centroids = np.asarray(metrics["epoch_centroids"])
    semantic_dispersion = np.asarray(metrics["semantic_dispersion"])
    innovation_velocity = np.asarray(metrics["innovation_velocity"])

    if epoch_labels.ndim != 1:
        raise ValueError("epoch_labels must be 1D")

    if epoch_counts.ndim != 1:
        raise ValueError("epoch_counts must be 1D")

    if epoch_centroids.ndim != 2:
        raise ValueError("epoch_centroids must be 2D")

    if semantic_dispersion.ndim != 1:
        raise ValueError("semantic_dispersion must be 1D")

    if innovation_velocity.ndim != 1:
        raise ValueError("innovation_velocity must be 1D")

    if len(epoch_labels) == 0:
        raise ValueError("epoch_labels must not be empty")

    if len(epoch_counts) != len(epoch_labels):
        raise ValueError("epoch_counts length must match epoch_labels")

    if len(semantic_dispersion) != len(epoch_labels):
        raise ValueError("semantic_dispersion length must match epoch_labels")

    if len(innovation_velocity) != max(len(epoch_labels) - 1, 0):
        raise ValueError("innovation_velocity length must equal epoch_count - 1")

    if epoch_centroids.shape[0] != len(epoch_labels):
        raise ValueError("epoch_centroids row count must match epoch_labels")

    if not np.isfinite(epoch_centroids).all():
        raise ValueError("epoch_centroids contains non-finite values")

    if not np.isfinite(semantic_dispersion).all():
        raise ValueError("semantic_dispersion contains non-finite values")

    if not np.isfinite(innovation_velocity).all():
        raise ValueError("innovation_velocity contains non-finite values")


def extract_epoch_table(metrics: dict[str, Any]) -> list[dict[str, float | int | str]]:
    validate_metrics_payload(metrics)

    labels = np.asarray(metrics["epoch_labels"])
    counts = np.asarray(metrics["epoch_counts"])
    dispersion = np.asarray(metrics["semantic_dispersion"])

    rows: list[dict[str, float | int | str]] = []
    for label, count, disp in zip(labels, counts, dispersion, strict=True):
        rows.append(
            {
                "epoch": str(label),
                "count": int(count),
                "dispersion": float(disp),
            }
        )
    return rows


def extract_velocity_table(metrics: dict[str, Any]) -> list[dict[str, float | str]]:
    validate_metrics_payload(metrics)

    labels = [str(x) for x in np.asarray(metrics["epoch_labels"]).tolist()]
    velocity = np.asarray(metrics["innovation_velocity"])

    rows: list[dict[str, float | str]] = []
    for idx, value in enumerate(velocity):
        left = labels[idx]
        right = labels[idx + 1]
        rows.append(
            {
                "transition": f"{left} -> {right}",
                "velocity": float(value),
            }
        )
    return rows


def summarize_route(route_name: str) -> dict[str, Any]:
    metrics = load_metrics(route_name)
    validate_metrics_payload(metrics)

    epoch_labels = [str(x) for x in np.asarray(metrics["epoch_labels"]).tolist()]
    epoch_counts = [int(x) for x in np.asarray(metrics["epoch_counts"]).tolist()]
    semantic_dispersion = [float(x) for x in np.asarray(metrics["semantic_dispersion"]).tolist()]
    innovation_velocity = [float(x) for x in np.asarray(metrics["innovation_velocity"]).tolist()]

    return {
        "route_name": str(np.asarray(metrics["route_name"]).item()),
        "corpus_name": str(np.asarray(metrics["corpus_name"]).item()),
        "epoch_count": len(epoch_labels),
        "epochs": epoch_labels,
        "epoch_counts": epoch_counts,
        "semantic_dispersion": semantic_dispersion,
        "innovation_velocity": innovation_velocity,
        "source_embedding_file_count": len(np.asarray(metrics["source_embedding_files"])),
    }