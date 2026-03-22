import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bins.s03_analysis.metrics import (  # noqa: E402
    CORPUS_NAME,
    EMBEDDING_DIM,
    METRIC_VERSION,
    MetricRecord,
    extract_metric_records_from_manifest_row,
    reload_and_validate_metrics_artifact,
    summarize_metrics_artifact_payload,
    validate_metrics_artifact_payload,
    validate_records_for_route,
    write_metrics_artifact,
)
from bins.s04_utils.artifacts import MetricsArtifact  # noqa: E402


def make_bundle(*, doc_id: str = "doc-1", route: str = "Route_A_Modern") -> dict[str, np.ndarray]:
    return {
        "doc_id": np.asarray(doc_id),
        "route": np.asarray(route),
        "section_labels": np.asarray(["A_intro", "A_methods"], dtype=object),
        "embeddings": np.vstack(
            [
                np.ones((EMBEDDING_DIM,), dtype=np.float32),
                np.full((EMBEDDING_DIM,), 2.0, dtype=np.float32),
            ]
        ).astype(np.float32),
        "source_path": np.asarray(f"data/structured/{route}/{doc_id}.json"),
    }


def make_artifact(*, route_name: str = "Route_A_Modern") -> MetricsArtifact:
    return MetricsArtifact(
        corpus_name=CORPUS_NAME,
        route_name=route_name,
        epoch_labels=["2025-2029"],
        epoch_counts=[2],
        epoch_centroids=np.ones((1, EMBEDDING_DIM), dtype=np.float32),
        semantic_dispersion=np.asarray([0.125], dtype=np.float32),
        innovation_velocity=np.asarray([], dtype=np.float32),
        source_embedding_files=[f"data/embeddings/{route_name}/doc-1.npz"],
        created_at_utc="2026-03-19T00:00:00+00:00",
        metric_version=METRIC_VERSION,
    )


class TestPostPhase5Validation(unittest.TestCase):
    def test_extract_metric_records_rejects_route_mismatch(self) -> None:
        bundle = make_bundle(route="Route_B_Legacy")
        manifest_row = {
            "doc_id": "doc-1",
            "route": "Route_A_Modern",
            "year": "2025",
        }

        with self.assertRaisesRegex(ValueError, "route mismatch"):
            extract_metric_records_from_manifest_row(
                bundle,
                manifest_row,
                source_file="data/embeddings/Route_A_Modern/doc-1.npz",
            )

    def test_validate_records_for_route_rejects_cross_route_mix(self) -> None:
        record_left = MetricRecord(
            doc_id="left",
            year=2025,
            vector=np.ones((EMBEDDING_DIM,), dtype=np.float32),
            source_file="left.npz",
            section_label="A_intro",
            route="Route_A_Modern",
        )
        record_right = MetricRecord(
            doc_id="right",
            year=2025,
            vector=np.ones((EMBEDDING_DIM,), dtype=np.float32),
            source_file="right.npz",
            section_label="A_methods",
            route="Route_B_Legacy",
        )

        with self.assertRaisesRegex(ValueError, "route mismatch"):
            validate_records_for_route(
                [record_left, record_right],
                route_name="Route_A_Modern",
            )

    def test_validate_metrics_artifact_accepts_singleton_epoch_payload(self) -> None:
        artifact = make_artifact()
        payload = {
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

        validate_metrics_artifact_payload(payload, expected_route_name="Route_A_Modern")
        summary = summarize_metrics_artifact_payload(payload)

        self.assertEqual(summary["epoch_count"], 1)
        self.assertTrue(summary["is_singleton_epoch_route"])
        self.assertEqual(summary["innovation_velocity_count"], 0)
        self.assertEqual(summary["total_section_embeddings"], 2)

    def test_validate_metrics_artifact_rejects_wrong_velocity_length(self) -> None:
        artifact = make_artifact()
        payload = {
            "corpus_name": np.asarray(artifact.corpus_name),
            "route_name": np.asarray(artifact.route_name),
            "epoch_labels": np.asarray(["2020-2024", "2025-2029"], dtype=object),
            "epoch_counts": np.asarray([2, 2], dtype=np.int32),
            "epoch_centroids": np.ones((2, EMBEDDING_DIM), dtype=np.float32),
            "semantic_dispersion": np.asarray([0.1, 0.2], dtype=np.float32),
            "innovation_velocity": np.asarray([], dtype=np.float32),
            "source_embedding_files": np.asarray(artifact.source_embedding_files, dtype=object),
            "created_at_utc": np.asarray(artifact.created_at_utc),
            "metric_version": np.asarray(artifact.metric_version),
        }

        with self.assertRaisesRegex(ValueError, "adjacent epoch pair count"):
            validate_metrics_artifact_payload(payload, expected_route_name="Route_A_Modern")

    def test_reload_and_validate_written_artifact(self) -> None:
        artifact = make_artifact()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "metrics.npz"
            write_metrics_artifact(artifact, output_path)
            payload = reload_and_validate_metrics_artifact(
                output_path,
                expected_route_name="Route_A_Modern",
                expected_corpus_name=CORPUS_NAME,
            )

        self.assertEqual(str(np.asarray(payload["route_name"]).item()), "Route_A_Modern")


if __name__ == "__main__":
    unittest.main()
