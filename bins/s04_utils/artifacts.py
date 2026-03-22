from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from bins.s04_utils.schemas import (
    A_INTRO,
    A_METHODS,
    A_RESULTS,
    ROUTE_LEGACY,
    ROUTE_MODERN,
    VALID_ROUTES,
)
from bins.s04_utils.validators import validate_structured_payload


@dataclass(frozen=True)
class StructuredSectionArtifact:
    doc_id: str
    source_filename: str
    source_pdf_path: str
    route: str
    year: int
    extraction_method: str
    page_count: int
    raw_text_length: int
    clean_text_length: int
    segmentation_strategy: str
    A_intro: str
    A_methods: str
    A_results: str

    def validate(self) -> None:
        payload = asdict(self)
        validate_structured_payload(payload)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        self.validate()
        return payload

    def write_json(self, output_path: Path) -> Path:
        self.validate()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return output_path

    @classmethod
    def from_json_path(cls, json_path: Path) -> "StructuredSectionArtifact":
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        artifact = cls(**payload)
        artifact.validate()
        return artifact


@dataclass(frozen=True)
class EmbeddingArtifact:
    doc_id: str
    route: str
    section_labels: tuple[str, ...]
    embeddings: np.ndarray
    source_path: str

    def validate(self) -> None:
        if self.route not in VALID_ROUTES:
            raise ValueError(f"Invalid route: {self.route}")

        if not self.doc_id.strip():
            raise ValueError("doc_id must not be empty")

        if self.embeddings.ndim != 2:
            raise ValueError(
                f"embeddings must be 2D, got shape {self.embeddings.shape}"
            )

        if self.embeddings.shape[0] != len(self.section_labels):
            raise ValueError(
                "section_labels length must equal embedding row count: "
                f"{len(self.section_labels)} vs {self.embeddings.shape[0]}"
            )

    def write_npz(self, output_path: Path) -> Path:
        self.validate()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        np.savez_compressed(
            output_path,
            doc_id=self.doc_id,
            route=self.route,
            section_labels=np.array(self.section_labels, dtype=object),
            embeddings=self.embeddings.astype(np.float32),
            source_path=self.source_path,
        )
        return output_path

    @classmethod
    def from_npz_path(cls, npz_path: Path) -> "EmbeddingArtifact":
        with np.load(npz_path, allow_pickle=True) as obj:
            artifact = cls(
                doc_id=str(obj["doc_id"]),
                route=str(obj["route"]),
                section_labels=tuple(str(x) for x in obj["section_labels"].tolist()),
                embeddings=np.asarray(obj["embeddings"], dtype=np.float32),
                source_path=str(obj["source_path"]),
            )
        artifact.validate()
        return artifact

@dataclass(frozen=True)
class MetricsArtifact:
    corpus_name: str
    route_name: str
    epoch_labels: tuple[str, ...]
    epoch_counts: tuple[int, ...]
    epoch_centroids: np.ndarray
    semantic_dispersion: np.ndarray
    innovation_velocity: np.ndarray
    source_embedding_files: tuple[str, ...]
    created_at_utc: str
    metric_version: str

    def validate(self) -> None:
        if not str(self.corpus_name).strip():
            raise ValueError("corpus_name must not be empty")

        if self.route_name not in VALID_ROUTES:
            raise ValueError(f"Invalid route_name: {self.route_name}")

        if not str(self.created_at_utc).strip():
            raise ValueError("created_at_utc must not be empty")

        if not str(self.metric_version).strip():
            raise ValueError("metric_version must not be empty")

        if len(self.epoch_labels) == 0:
            raise ValueError("epoch_labels must not be empty")

        if len(self.epoch_counts) != len(self.epoch_labels):
            raise ValueError(
                "epoch_counts length must equal epoch_labels length: "
                f"{len(self.epoch_counts)} vs {len(self.epoch_labels)}"
            )

        if any(int(x) <= 0 for x in self.epoch_counts):
            raise ValueError("epoch_counts must contain only positive integers")

        epoch_centroids = np.asarray(self.epoch_centroids, dtype=np.float32)
        semantic_dispersion = np.asarray(self.semantic_dispersion, dtype=np.float32)
        innovation_velocity = np.asarray(self.innovation_velocity, dtype=np.float32)

        if epoch_centroids.ndim != 2:
            raise ValueError(
                f"epoch_centroids must be 2D, got shape {epoch_centroids.shape}"
            )

        if epoch_centroids.shape[0] != len(self.epoch_labels):
            raise ValueError(
                "epoch_centroids row count must equal epoch_labels length: "
                f"{epoch_centroids.shape[0]} vs {len(self.epoch_labels)}"
            )

        if semantic_dispersion.ndim != 1:
            raise ValueError(
                f"semantic_dispersion must be 1D, got shape {semantic_dispersion.shape}"
            )

        if semantic_dispersion.shape[0] != len(self.epoch_labels):
            raise ValueError(
                "semantic_dispersion length must equal epoch_labels length: "
                f"{semantic_dispersion.shape[0]} vs {len(self.epoch_labels)}"
            )

        expected_velocity_len = max(len(self.epoch_labels) - 1, 0)
        if innovation_velocity.ndim != 1:
            raise ValueError(
                f"innovation_velocity must be 1D, got shape {innovation_velocity.shape}"
            )

        if innovation_velocity.shape[0] != expected_velocity_len:
            raise ValueError(
                "innovation_velocity length must equal adjacent epoch pair count: "
                f"{innovation_velocity.shape[0]} vs {expected_velocity_len}"
            )

        if not np.isfinite(epoch_centroids).all():
            raise ValueError("epoch_centroids contains non-finite values")

        if not np.isfinite(semantic_dispersion).all():
            raise ValueError("semantic_dispersion contains non-finite values")

        if not np.isfinite(innovation_velocity).all():
            raise ValueError("innovation_velocity contains non-finite values")

        if any(not str(x).strip() for x in self.source_embedding_files):
            raise ValueError("source_embedding_files must not contain empty values")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "corpus_name": self.corpus_name,
            "route_name": self.route_name,
            "epoch_labels": list(self.epoch_labels),
            "epoch_counts": list(self.epoch_counts),
            "epoch_centroids": np.asarray(self.epoch_centroids, dtype=np.float32),
            "semantic_dispersion": np.asarray(self.semantic_dispersion, dtype=np.float32),
            "innovation_velocity": np.asarray(self.innovation_velocity, dtype=np.float32),
            "source_embedding_files": list(self.source_embedding_files),
            "created_at_utc": self.created_at_utc,
            "metric_version": self.metric_version,
        }

    def write_npz(self, output_path: Path) -> Path:
        self.validate()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        np.savez_compressed(
            output_path,
            corpus_name=np.asarray(self.corpus_name),
            route_name=np.asarray(self.route_name),
            epoch_labels=np.asarray(self.epoch_labels, dtype=object),
            epoch_counts=np.asarray(self.epoch_counts, dtype=np.int32),
            epoch_centroids=np.asarray(self.epoch_centroids, dtype=np.float32),
            semantic_dispersion=np.asarray(self.semantic_dispersion, dtype=np.float32),
            innovation_velocity=np.asarray(self.innovation_velocity, dtype=np.float32),
            source_embedding_files=np.asarray(self.source_embedding_files, dtype=object),
            created_at_utc=np.asarray(self.created_at_utc),
            metric_version=np.asarray(self.metric_version),
        )
        return output_path

    @classmethod
    def from_npz_path(cls, npz_path: Path) -> "MetricsArtifact":
        with np.load(npz_path, allow_pickle=True) as obj:
            artifact = cls(
                corpus_name=str(obj["corpus_name"]),
                route_name=str(obj["route_name"]),
                epoch_labels=tuple(str(x) for x in obj["epoch_labels"].tolist()),
                epoch_counts=tuple(int(x) for x in obj["epoch_counts"].tolist()),
                epoch_centroids=np.asarray(obj["epoch_centroids"], dtype=np.float32),
                semantic_dispersion=np.asarray(obj["semantic_dispersion"], dtype=np.float32),
                innovation_velocity=np.asarray(obj["innovation_velocity"], dtype=np.float32),
                source_embedding_files=tuple(str(x) for x in obj["source_embedding_files"].tolist()),
                created_at_utc=str(obj["created_at_utc"]),
                metric_version=str(obj["metric_version"]),
            )
        artifact.validate()
        return artifact
    
def resolve_embedding_output_dir(
    route: str,
    modern_dir: Path,
    legacy_dir: Path,
) -> Path:
    if route == ROUTE_MODERN:
        return modern_dir
    if route == ROUTE_LEGACY:
        return legacy_dir
    raise ValueError(f"Unrecognized route: {route}")


def build_structured_section_artifact(
    *,
    doc_id: str,
    source_filename: str,
    source_pdf_path: str,
    route: str,
    year: int,
    extraction_method: str,
    page_count: int,
    raw_text_length: int,
    clean_text_length: int,
    segmentation_strategy: str,
    sections: dict[str, str],
) -> StructuredSectionArtifact:
    artifact = StructuredSectionArtifact(
        doc_id=doc_id,
        source_filename=source_filename,
        source_pdf_path=source_pdf_path,
        route=route,
        year=year,
        extraction_method=extraction_method,
        page_count=page_count,
        raw_text_length=raw_text_length,
        clean_text_length=clean_text_length,
        segmentation_strategy=segmentation_strategy,
        A_intro=str(sections.get(A_INTRO, "")).strip(),
        A_methods=str(sections.get(A_METHODS, "")).strip(),
        A_results=str(sections.get(A_RESULTS, "")).strip(),
    )
    artifact.validate()
    return artifact