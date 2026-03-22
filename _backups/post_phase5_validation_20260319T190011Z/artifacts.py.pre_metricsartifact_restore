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