from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial.distance import cdist

from bins.s04_utils.artifacts import MetricsArtifact
from bins.s04_utils.manifest_manager import (
    get_metric_eligible_records,
    mark_metrics_failure,
    mark_metrics_success,
    utc_now_iso,
)
from bins.s04_utils.schemas import (
    EMBEDDING_BUNDLE_KEY_DOC_ID,
    EMBEDDING_BUNDLE_KEY_EMBEDDINGS,
    EMBEDDING_BUNDLE_KEY_ROUTE,
    EMBEDDING_BUNDLE_KEY_SECTION_LABELS,
    EMBEDDING_BUNDLE_KEY_SOURCE_PATH,
    EMBEDDING_BUNDLE_REQUIRED_KEYS,
)

EMBEDDING_DIM = 768
EPOCH_WIDTH = 5
METRIC_VERSION = "0.1.0"
CORPUS_NAME = "JAE_Legacy_Audit"

METRICS_ARTIFACT_REQUIRED_KEYS = frozenset(
    {
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
)


@dataclass(slots=True)
class MetricRecord:
    doc_id: str
    year: int
    vector: np.ndarray
    source_file: str
    section_label: str
    route: str


def _row_get(row: Any, field: str) -> str:
    if isinstance(row, Mapping):
        value: Any = row.get(field, "")
    else:
        value = getattr(row, field, "")
    return "" if value is None else str(value)


def _row_doc_id(row: Any) -> str:
    return _row_get(row, "doc_id").strip()


def _row_route(row: Any) -> str:
    return _row_get(row, "route").strip()


def _parse_scalar_text(value: Any, *, field_name: str) -> str:
    array_value = np.asarray(value)
    if array_value.shape != ():
        raise ValueError(f"{field_name} must be scalar, got shape {array_value.shape}")

    text = str(array_value.item()).strip()
    if not text:
        raise ValueError(f"{field_name} must not be empty")

    return text


def _parse_epoch_label_start(label: str) -> int:
    parts = label.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid epoch label format: {label!r}")

    try:
        start = int(parts[0])
        end = int(parts[1])
    except ValueError as exc:
        raise ValueError(f"Epoch label must contain integer bounds: {label!r}") from exc

    if end < start:
        raise ValueError(f"Epoch label end precedes start: {label!r}")

    if (end - start + 1) != EPOCH_WIDTH:
        raise ValueError(
            f"Epoch label width must equal {EPOCH_WIDTH}, got {label!r}"
        )

    return start


def load_embedding_bundle(bundle_path: Path) -> dict[str, Any]:
    if not bundle_path.exists():
        raise FileNotFoundError(f"Embedding bundle not found: {bundle_path}")
    if bundle_path.suffix != ".npz":
        raise ValueError(f"Unsupported embedding bundle type: {bundle_path.suffix}")

    with np.load(bundle_path, allow_pickle=True) as data:
        bundle: dict[str, Any] = {}
        for key in data.files:
            bundle[str(key)] = data[key]
        return bundle


def validate_embedding_bundle(bundle: dict[str, Any]) -> None:
    missing = EMBEDDING_BUNDLE_REQUIRED_KEYS - set(bundle.keys())
    if missing:
        raise ValueError(f"Embedding bundle missing required keys: {sorted(missing)}")

    doc_id = np.asarray(bundle[EMBEDDING_BUNDLE_KEY_DOC_ID])
    route = np.asarray(bundle[EMBEDDING_BUNDLE_KEY_ROUTE])
    section_labels = np.asarray(bundle[EMBEDDING_BUNDLE_KEY_SECTION_LABELS])
    embeddings = np.asarray(bundle[EMBEDDING_BUNDLE_KEY_EMBEDDINGS])
    source_path = np.asarray(bundle[EMBEDDING_BUNDLE_KEY_SOURCE_PATH])

    if doc_id.shape != ():
        raise ValueError(f"doc_id must be scalar, got shape {doc_id.shape}")
    if route.shape != ():
        raise ValueError(f"route must be scalar, got shape {route.shape}")
    if source_path.shape != ():
        raise ValueError(f"source_path must be scalar, got shape {source_path.shape}")

    if not str(doc_id.item()).strip():
        raise ValueError("doc_id must not be empty")
    if not str(route.item()).strip():
        raise ValueError("route must not be empty")
    if not str(source_path.item()).strip():
        raise ValueError("source_path must not be empty")

    if section_labels.ndim != 1:
        raise ValueError("section_labels must be a 1D array")

    if embeddings.ndim != 2:
        raise ValueError("embeddings must be a 2D array")

    if embeddings.shape[0] == 0:
        raise ValueError("embeddings array is empty")

    if embeddings.shape[1] != EMBEDDING_DIM:
        raise ValueError(
            f"Expected embedding width {EMBEDDING_DIM}, got {embeddings.shape[1]}"
        )

    if embeddings.dtype != np.float32:
        raise ValueError(f"embeddings dtype must be float32, got {embeddings.dtype}")

    if len(section_labels) != embeddings.shape[0]:
        raise ValueError("section_labels length must match embeddings row count")

    normalized_labels = [str(label).strip() for label in section_labels.tolist()]
    if any(not label for label in normalized_labels):
        raise ValueError("section_labels must not contain empty values")

    if not np.isfinite(embeddings).all():
        raise ValueError("embeddings must contain only finite values")


def extract_metric_records(
    bundle: dict[str, Any],
    *,
    year: int,
    source_file: str,
) -> list[MetricRecord]:
    validate_embedding_bundle(bundle)

    if not source_file.strip():
        raise ValueError("source_file must be provided for metric record extraction")

    doc_id = str(np.asarray(bundle[EMBEDDING_BUNDLE_KEY_DOC_ID]).item())
    route = str(np.asarray(bundle[EMBEDDING_BUNDLE_KEY_ROUTE]).item())
    section_labels = np.asarray(bundle[EMBEDDING_BUNDLE_KEY_SECTION_LABELS])
    embeddings = np.asarray(bundle[EMBEDDING_BUNDLE_KEY_EMBEDDINGS]).astype(
        np.float32, copy=False
    )

    records: list[MetricRecord] = []

    for section_label, vector in zip(section_labels, embeddings, strict=True):
        vector = np.asarray(vector).astype(np.float32, copy=False)
        if vector.shape != (EMBEDDING_DIM,):
            raise ValueError(f"Record vector has invalid shape: {vector.shape}")

        records.append(
            MetricRecord(
                doc_id=doc_id,
                year=int(year),
                vector=vector,
                source_file=source_file,
                section_label=str(section_label).strip(),
                route=route,
            )
        )

    if not records:
        raise ValueError("No metric records extracted from embedding bundle")

    return records


def extract_metric_records_from_manifest_row(
    bundle: dict[str, Any],
    manifest_row: Any,
    *,
    source_file: str,
) -> list[MetricRecord]:
    validate_embedding_bundle(bundle)

    doc_id = str(np.asarray(bundle[EMBEDDING_BUNDLE_KEY_DOC_ID]).item())
    manifest_doc_id = _row_get(manifest_row, "doc_id").strip()

    if manifest_doc_id != doc_id:
        raise ValueError(
            f"Manifest row doc_id mismatch: bundle={doc_id}, manifest={manifest_doc_id}"
        )

    bundle_route = str(np.asarray(bundle[EMBEDDING_BUNDLE_KEY_ROUTE]).item()).strip()
    manifest_route = _row_get(manifest_row, "route").strip()

    if not manifest_route:
        raise ValueError(f"Manifest row missing route for doc_id={doc_id}")

    if bundle_route != manifest_route:
        raise ValueError(
            f"Manifest row route mismatch: bundle={bundle_route}, manifest={manifest_route}, doc_id={doc_id}"
        )

    year_raw = _row_get(manifest_row, "year").strip()
    if not year_raw:
        raise ValueError(f"Manifest row missing year for doc_id={doc_id}")

    try:
        year = int(year_raw)
    except ValueError as exc:
        raise ValueError(
            f"Manifest year must be an integer for doc_id={doc_id}, got {year_raw!r}"
        ) from exc

    return extract_metric_records(
        bundle,
        year=year,
        source_file=source_file,
    )


def assign_epoch(year: int, width: int = EPOCH_WIDTH) -> tuple[int, int]:
    if width <= 0:
        raise ValueError("Epoch width must be positive")

    start = year - ((year - 1960) % width)
    end = start + width - 1
    return start, end


def format_epoch_label(epoch: tuple[int, int]) -> str:
    start, end = epoch
    return f"{start}-{end}"


def group_vectors_by_epoch(records: list[MetricRecord]) -> dict[str, np.ndarray]:
    if not records:
        raise ValueError("Cannot group an empty record set")

    grouped: dict[str, list[np.ndarray]] = {}
    for record in records:
        label = format_epoch_label(assign_epoch(record.year))
        grouped.setdefault(label, []).append(record.vector)

    ordered_labels = sorted(grouped.keys(), key=lambda x: int(x.split("-")[0]))
    return {
        label: np.vstack(grouped[label]).astype(np.float32)
        for label in ordered_labels
    }


def compute_epoch_centroid(epoch_vectors: np.ndarray) -> np.ndarray:
    if epoch_vectors.ndim != 2:
        raise ValueError("Epoch vectors must be 2D")
    if len(epoch_vectors) == 0:
        raise ValueError("Epoch vectors cannot be empty")

    return np.asarray(np.mean(epoch_vectors, axis=0), dtype=np.float32)


def compute_semantic_dispersion(epoch_vectors: np.ndarray, centroid: np.ndarray) -> float:
    if epoch_vectors.ndim != 2:
        raise ValueError("Epoch vectors must be 2D")

    centroid_2d = np.asarray(centroid, dtype=np.float32).reshape(1, -1)
    distances = cdist(epoch_vectors, centroid_2d, metric="cosine")
    return float(np.mean(distances))


def compute_innovation_velocity(
    epoch_centroids: dict[str, np.ndarray]
) -> dict[str, float]:
    labels = list(epoch_centroids.keys())
    velocities: dict[str, float] = {}

    for idx in range(len(labels) - 1):
        left = labels[idx]
        right = labels[idx + 1]
        pair_key = f"{left}__to__{right}"

        left_centroid = np.asarray(epoch_centroids[left], dtype=np.float32).reshape(1, -1)
        right_centroid = np.asarray(epoch_centroids[right], dtype=np.float32).reshape(1, -1)

        distance = cdist(left_centroid, right_centroid, metric="cosine")[0, 0]
        velocities[pair_key] = float(distance)

    return velocities


def compute_epoch_metrics(grouped_vectors: dict[str, np.ndarray]) -> dict[str, Any]:
    if not grouped_vectors:
        raise ValueError("No grouped vectors provided")

    epoch_labels = list(grouped_vectors.keys())
    epoch_counts: list[int] = []
    epoch_centroids: dict[str, np.ndarray] = {}
    semantic_dispersion: dict[str, float] = {}

    for label in epoch_labels:
        vectors = grouped_vectors[label]
        centroid = compute_epoch_centroid(vectors)
        dispersion = compute_semantic_dispersion(vectors, centroid)

        epoch_counts.append(int(len(vectors)))
        epoch_centroids[label] = centroid
        semantic_dispersion[label] = dispersion

    innovation_velocity = compute_innovation_velocity(epoch_centroids)

    return {
        "epoch_labels": epoch_labels,
        "epoch_counts": epoch_counts,
        "epoch_centroids": epoch_centroids,
        "semantic_dispersion": semantic_dispersion,
        "innovation_velocity": innovation_velocity,
    }


def collect_source_embedding_files(records: list[MetricRecord]) -> list[str]:
    return sorted({record.source_file for record in records})


def build_metrics_payload(records: list[MetricRecord]) -> dict[str, Any]:
    grouped = group_vectors_by_epoch(records)
    metrics = compute_epoch_metrics(grouped)
    metrics["source_embedding_files"] = collect_source_embedding_files(records)
    metrics["metric_version"] = METRIC_VERSION
    return metrics


def validate_records_for_route(records: list[MetricRecord], *, route_name: str) -> None:
    if not records:
        raise ValueError("MetricRecord collection must not be empty")

    observed_routes = sorted({record.route for record in records})
    if observed_routes != [route_name]:
        raise ValueError(
            f"MetricRecord route mismatch: expected={route_name}, observed={observed_routes}"
        )

    for record in records:
        if record.vector.shape != (EMBEDDING_DIM,):
            raise ValueError(
                f"MetricRecord vector shape mismatch for doc_id={record.doc_id}: {record.vector.shape}"
            )
        if not np.isfinite(record.vector).all():
            raise ValueError(
                f"MetricRecord vector contains non-finite values for doc_id={record.doc_id}"
            )
        if not record.section_label.strip():
            raise ValueError(f"MetricRecord section_label missing for doc_id={record.doc_id}")
        if not record.source_file.strip():
            raise ValueError(f"MetricRecord source_file missing for doc_id={record.doc_id}")


def build_metrics_artifact(
    records: list[MetricRecord],
    *,
    route_name: str,
    corpus_name: str = CORPUS_NAME,
) -> MetricsArtifact:
    validate_records_for_route(records, route_name=route_name)

    payload = build_metrics_payload(records)
    epoch_labels = payload["epoch_labels"]

    epoch_centroids = np.vstack(
        [payload["epoch_centroids"][label] for label in epoch_labels]
    ).astype(np.float32, copy=False)

    semantic_dispersion = np.asarray(
        [payload["semantic_dispersion"][label] for label in epoch_labels],
        dtype=np.float32,
    )

    innovation_velocity = np.asarray(
        list(payload["innovation_velocity"].values()),
        dtype=np.float32,
    )

    artifact = MetricsArtifact(
        corpus_name=corpus_name,
        route_name=route_name,
        epoch_labels=tuple(str(label) for label in epoch_labels),
        epoch_counts=tuple(int(count) for count in payload["epoch_counts"]),
        epoch_centroids=epoch_centroids,
        semantic_dispersion=semantic_dispersion,
        innovation_velocity=innovation_velocity,
        source_embedding_files=tuple(
            str(path) for path in payload["source_embedding_files"]
        ),
        created_at_utc=utc_now_iso(),
        metric_version=METRIC_VERSION,
    )

    validate_metrics_artifact_instance(artifact, expected_route_name=route_name)
    return artifact


def build_metrics_output_path(route_name: str) -> Path:
    return Path("data/metrics") / route_name / "metrics.npz"


def ensure_metrics_output_dir(route_name: str) -> Path:
    output_dir = Path("data/metrics") / route_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_metrics_artifact(artifact: MetricsArtifact, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        output_path,
        corpus_name=np.asarray(artifact.corpus_name),
        route_name=np.asarray(artifact.route_name),
        epoch_labels=np.asarray(artifact.epoch_labels, dtype=object),
        epoch_counts=np.asarray(artifact.epoch_counts, dtype=np.int32),
        epoch_centroids=np.asarray(artifact.epoch_centroids, dtype=np.float32),
        semantic_dispersion=np.asarray(artifact.semantic_dispersion, dtype=np.float32),
        innovation_velocity=np.asarray(artifact.innovation_velocity, dtype=np.float32),
        source_embedding_files=np.asarray(artifact.source_embedding_files, dtype=object),
        created_at_utc=np.asarray(artifact.created_at_utc),
        metric_version=np.asarray(artifact.metric_version),
    )

    if not output_path.exists():
        raise FileNotFoundError(f"Metrics artifact write failed: {output_path}")


def load_metrics_artifact_payload(metrics_path: Path) -> dict[str, Any]:
    if not metrics_path.exists():
        raise FileNotFoundError(f"Metrics artifact not found: {metrics_path}")
    if metrics_path.suffix != ".npz":
        raise ValueError(f"Unsupported metrics artifact type: {metrics_path.suffix}")

    with np.load(metrics_path, allow_pickle=True) as data:
        payload: dict[str, Any] = {}
        for key in data.files:
            payload[str(key)] = data[key]
        return payload


def validate_metrics_artifact_payload(
    payload: dict[str, Any],
    *,
    expected_route_name: str | None = None,
    expected_corpus_name: str | None = CORPUS_NAME,
) -> None:
    missing = METRICS_ARTIFACT_REQUIRED_KEYS - set(payload.keys())
    if missing:
        raise ValueError(f"Metrics artifact missing required keys: {sorted(missing)}")

    unexpected = set(payload.keys()) - METRICS_ARTIFACT_REQUIRED_KEYS
    if unexpected:
        raise ValueError(f"Metrics artifact contains unexpected keys: {sorted(unexpected)}")

    corpus_name = _parse_scalar_text(payload["corpus_name"], field_name="corpus_name")
    route_name = _parse_scalar_text(payload["route_name"], field_name="route_name")
    _parse_scalar_text(payload["created_at_utc"], field_name="created_at_utc")
    metric_version = _parse_scalar_text(payload["metric_version"], field_name="metric_version")

    if expected_corpus_name is not None and corpus_name != expected_corpus_name:
        raise ValueError(
            f"Metrics artifact corpus_name mismatch: expected={expected_corpus_name}, got={corpus_name}"
        )
    if expected_route_name is not None and route_name != expected_route_name:
        raise ValueError(
            f"Metrics artifact route_name mismatch: expected={expected_route_name}, got={route_name}"
        )
    if metric_version != METRIC_VERSION:
        raise ValueError(
            f"Metrics artifact version mismatch: expected={METRIC_VERSION}, got={metric_version}"
        )

    epoch_labels_array = np.asarray(payload["epoch_labels"])
    epoch_counts_array = np.asarray(payload["epoch_counts"])
    epoch_centroids_array = np.asarray(payload["epoch_centroids"])
    semantic_dispersion_array = np.asarray(payload["semantic_dispersion"])
    innovation_velocity_array = np.asarray(payload["innovation_velocity"])
    source_embedding_files_array = np.asarray(payload["source_embedding_files"])

    if epoch_labels_array.ndim != 1:
        raise ValueError("epoch_labels must be a 1D array")
    if len(epoch_labels_array) == 0:
        raise ValueError("epoch_labels must not be empty")

    epoch_labels = [str(label).strip() for label in epoch_labels_array.tolist()]
    if any(not label for label in epoch_labels):
        raise ValueError("epoch_labels must not contain empty values")
    if len(set(epoch_labels)) != len(epoch_labels):
        raise ValueError("epoch_labels must be unique")

    epoch_starts = [_parse_epoch_label_start(label) for label in epoch_labels]
    if epoch_starts != sorted(epoch_starts):
        raise ValueError("epoch_labels must be sorted by ascending epoch start year")

    if epoch_counts_array.ndim != 1:
        raise ValueError("epoch_counts must be a 1D array")
    if len(epoch_counts_array) != len(epoch_labels):
        raise ValueError("epoch_counts length must match epoch_labels length")
    if np.any(epoch_counts_array <= 0):
        raise ValueError("epoch_counts must contain only positive integers")

    if epoch_centroids_array.ndim != 2:
        raise ValueError("epoch_centroids must be a 2D array")
    if epoch_centroids_array.shape != (len(epoch_labels), EMBEDDING_DIM):
        raise ValueError(
            "epoch_centroids shape must equal "
            f"({len(epoch_labels)}, {EMBEDDING_DIM}), got {epoch_centroids_array.shape}"
        )

    if semantic_dispersion_array.ndim != 1:
        raise ValueError("semantic_dispersion must be a 1D array")
    if len(semantic_dispersion_array) != len(epoch_labels):
        raise ValueError(
            "semantic_dispersion length must match epoch_labels length"
        )

    expected_velocity_length = max(len(epoch_labels) - 1, 0)
    if innovation_velocity_array.ndim != 1:
        raise ValueError("innovation_velocity must be a 1D array")
    if len(innovation_velocity_array) != expected_velocity_length:
        raise ValueError(
            "innovation_velocity length must equal adjacent epoch pair count "
            f"({expected_velocity_length}), got {len(innovation_velocity_array)}"
        )

    if source_embedding_files_array.ndim != 1:
        raise ValueError("source_embedding_files must be a 1D array")
    if len(source_embedding_files_array) == 0:
        raise ValueError("source_embedding_files must not be empty")

    source_embedding_files = [
        str(path).strip() for path in source_embedding_files_array.tolist()
    ]
    if any(not path for path in source_embedding_files):
        raise ValueError("source_embedding_files must not contain empty values")
    if source_embedding_files != sorted(set(source_embedding_files)):
        raise ValueError("source_embedding_files must be unique and sorted deterministically")

    if not np.isfinite(epoch_centroids_array).all():
        raise ValueError("epoch_centroids must contain only finite values")
    if not np.isfinite(semantic_dispersion_array).all():
        raise ValueError("semantic_dispersion must contain only finite values")
    if not np.isfinite(innovation_velocity_array).all():
        raise ValueError("innovation_velocity must contain only finite values")


def validate_metrics_artifact_instance(
    artifact: MetricsArtifact,
    *,
    expected_route_name: str | None = None,
    expected_corpus_name: str | None = CORPUS_NAME,
) -> None:
    payload: dict[str, Any] = {
        "corpus_name": np.asarray(artifact.corpus_name),
        "route_name": np.asarray(artifact.route_name),
        "epoch_labels": np.asarray(artifact.epoch_labels, dtype=object),
        "epoch_counts": np.asarray(artifact.epoch_counts, dtype=np.int32),
        "epoch_centroids": np.asarray(artifact.epoch_centroids, dtype=np.float32),
        "semantic_dispersion": np.asarray(artifact.semantic_dispersion, dtype=np.float32),
        "innovation_velocity": np.asarray(artifact.innovation_velocity, dtype=np.float32),
        "source_embedding_files": np.asarray(artifact.source_embedding_files, dtype=object),
        "created_at_utc": np.asarray(artifact.created_at_utc),
        "metric_version": np.asarray(artifact.metric_version),
    }
    validate_metrics_artifact_payload(
        payload,
        expected_route_name=expected_route_name,
        expected_corpus_name=expected_corpus_name,
    )


def reload_and_validate_metrics_artifact(
    metrics_path: Path,
    *,
    expected_route_name: str | None = None,
    expected_corpus_name: str | None = CORPUS_NAME,
) -> dict[str, Any]:
    payload: dict[str, Any] = load_metrics_artifact_payload(metrics_path)
    validate_metrics_artifact_payload(
        payload,
        expected_route_name=expected_route_name,
        expected_corpus_name=expected_corpus_name,
    )
    return payload


def summarize_metrics_artifact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    validate_metrics_artifact_payload(payload)

    epoch_labels = [str(label) for label in np.asarray(payload["epoch_labels"]).tolist()]
    epoch_counts = np.asarray(payload["epoch_counts"], dtype=np.int32)
    innovation_velocity = np.asarray(payload["innovation_velocity"], dtype=np.float32)
    source_embedding_files = [
        str(path) for path in np.asarray(payload["source_embedding_files"]).tolist()
    ]

    return {
        "corpus_name": _parse_scalar_text(payload["corpus_name"], field_name="corpus_name"),
        "route_name": _parse_scalar_text(payload["route_name"], field_name="route_name"),
        "metric_version": _parse_scalar_text(payload["metric_version"], field_name="metric_version"),
        "epoch_count": len(epoch_labels),
        "first_epoch": epoch_labels[0],
        "last_epoch": epoch_labels[-1],
        "total_section_embeddings": int(np.sum(epoch_counts)),
        "source_embedding_file_count": len(source_embedding_files),
        "innovation_velocity_count": int(len(innovation_velocity)),
        "is_singleton_epoch_route": len(epoch_labels) == 1,
    }


def process_route_metrics(
    route_name: str,
    manifest_rows: list[Any],
) -> Path:
    if not manifest_rows:
        raise ValueError(f"No manifest rows provided for route={route_name}")

    records: list[MetricRecord] = []
    embedding_root = Path("data/embeddings") / route_name

    if not embedding_root.exists():
        raise FileNotFoundError(f"Embedding directory not found: {embedding_root}")

    for row in sorted(manifest_rows, key=_row_doc_id):
        doc_id = _row_doc_id(row)
        row_route = _row_route(row)

        if row_route != route_name:
            raise ValueError(
                f"Route mismatch while processing metrics: expected={route_name}, got={row_route}, doc_id={doc_id}"
            )

        matches: list[Path] = list(embedding_root.rglob(f"{doc_id}.npz"))

        if len(matches) == 0:
            raise FileNotFoundError(
                f"Embedding bundle not found for doc_id={doc_id} under {embedding_root}"
            )

        if len(matches) > 1:
            raise RuntimeError(
                f"Multiple embedding bundles found for doc_id={doc_id}: {matches}"
            )

        bundle_path = matches[0]
        bundle = load_embedding_bundle(bundle_path)

        doc_records = extract_metric_records_from_manifest_row(
            bundle,
            row,
            source_file=str(bundle_path),
        )
        records.extend(doc_records)

    if not records:
        raise RuntimeError(f"No metric records generated for route={route_name}")

    artifact = build_metrics_artifact(records, route_name=route_name)

    ensure_metrics_output_dir(route_name)
    output_path = build_metrics_output_path(route_name)
    write_metrics_artifact(artifact, output_path)

    reload_and_validate_metrics_artifact(
        output_path,
        expected_route_name=route_name,
        expected_corpus_name=CORPUS_NAME,
    )

    return output_path


def run_phase5_metrics() -> None:
    eligible_rows = get_metric_eligible_records()
    if not eligible_rows:
        print("No Phase 5-eligible manifest rows found.")
        return

    rows_by_route: dict[str, list[Any]] = {}
    for row in eligible_rows:
        route_name = _row_route(row)
        if not route_name:
            doc_id = _row_doc_id(row)
            mark_metrics_failure(doc_id, f"Missing route for doc_id={doc_id}")
            continue
        rows_by_route.setdefault(route_name, []).append(row)

    for route_name in sorted(rows_by_route.keys()):
        route_rows = rows_by_route[route_name]
        route_doc_ids = [_row_doc_id(row) for row in route_rows]

        try:
            output_path = process_route_metrics(route_name, route_rows)

            for doc_id in route_doc_ids:
                mark_metrics_success(doc_id)

            print(f"[OK] route={route_name} -> {output_path}")
        except Exception as exc:
            for doc_id in route_doc_ids:
                mark_metrics_failure(doc_id, str(exc))

            print(f"[FAIL] route={route_name} -> {exc}")


if __name__ == "__main__":
    run_phase5_metrics()