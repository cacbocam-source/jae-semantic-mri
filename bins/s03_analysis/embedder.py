from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol, cast

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer
from transformers.modeling_outputs import BaseModelOutput

from config import (
    DEVICE,
    MODEL_ID,
    STRUCTURED_DIR,
    EMBEDDINGS_DIR,
    EMBEDDINGS_ROUTE_MODERN,
    EMBEDDINGS_ROUTE_LEGACY,
)
from bins.s04_utils.artifacts import (
    EmbeddingArtifact,
    StructuredSectionArtifact,
    resolve_embedding_output_dir,
)
from bins.s04_utils.manifest_manager import (
    ManifestRecord,
    mark_stage_failure,
    mark_stage_skipped,
    mark_stage_success,
    upsert_record,
)
from bins.s04_utils.schemas import A_INTRO, A_RESULTS
from bins.s04_utils.validators import is_real_section_text

EMBED_DIM = 768
SECTION_KEYS = (A_INTRO, A_RESULTS)


class TokenizerProtocol(Protocol):
    def __call__(
        self,
        texts: list[str],
        *,
        padding: bool,
        truncation: bool,
        max_length: int,
        return_tensors: str,
    ) -> dict[str, torch.Tensor]: ...


class ModelProtocol(Protocol):
    def to(self, device: str) -> "ModelProtocol": ...
    def eval(self) -> "ModelProtocol": ...
    def __call__(self, **kwargs: torch.Tensor) -> BaseModelOutput: ...


@dataclass(frozen=True)
class StructuredRecord:
    doc_id: str
    route: str
    section_texts: dict[str, str]
    source_path: Path


def iter_structured_json_files(structured_dir: Path) -> Iterable[Path]:
    yield from sorted(structured_dir.rglob("*.json"))


def load_structured_record(json_path: Path) -> StructuredRecord:
    artifact = StructuredSectionArtifact.from_json_path(json_path)

    section_texts = {
        A_INTRO: artifact.A_intro,
        A_RESULTS: artifact.A_results,
    }

    return StructuredRecord(
        doc_id=artifact.doc_id,
        route=artifact.route,
        section_texts=section_texts,
        source_path=json_path,
    )


def resolve_output_path(record: StructuredRecord) -> Path:
    output_dir = resolve_embedding_output_dir(
        record.route,
        modern_dir=EMBEDDINGS_ROUTE_MODERN,
        legacy_dir=EMBEDDINGS_ROUTE_LEGACY,
    )
    return output_dir / f"{record.doc_id}.npz"


def mean_pool(
    last_hidden_state: torch.Tensor,
    attention_mask: torch.Tensor,
) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    masked_embeddings = last_hidden_state * mask
    summed = masked_embeddings.sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return summed / counts


def l2_normalize(vectors: torch.Tensor) -> torch.Tensor:
    return torch.nn.functional.normalize(vectors, p=2, dim=1)


def load_model() -> tuple[TokenizerProtocol, ModelProtocol]:
    tokenizer = cast(
        TokenizerProtocol,
        AutoTokenizer.from_pretrained(  # pyright: ignore[reportUnknownMemberType]
            MODEL_ID,
            trust_remote_code=True,
        ),
    )

    model = cast(
        ModelProtocol,
        AutoModel.from_pretrained(  # pyright: ignore[reportUnknownMemberType]
            MODEL_ID,
            trust_remote_code=True,
        ),
    )

    model = model.to(DEVICE)
    model = model.eval()

    return tokenizer, model


@torch.inference_mode()
def embed_texts(
    texts: list[str],
    tokenizer: TokenizerProtocol,
    model: ModelProtocol,
    max_length: int = 8192,
) -> np.ndarray:
    if not texts:
        raise ValueError("texts must not be empty")

    encoded: dict[str, torch.Tensor] = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
    )

    encoded = {key: value.to(DEVICE) for key, value in encoded.items()}
    outputs: BaseModelOutput = model(**encoded)

    if outputs.last_hidden_state is None:
        raise ValueError("Model output missing last_hidden_state")

    pooled = mean_pool(outputs.last_hidden_state, encoded["attention_mask"])
    normalized = l2_normalize(pooled)

    array = normalized.detach().cpu().numpy().astype(np.float32)

    if array.ndim != 2:
        raise ValueError(f"Expected 2D embedding array, got shape {array.shape}")

    if array.shape[1] != EMBED_DIM:
        raise ValueError(
            f"Expected embedding dimension {EMBED_DIM} for model {MODEL_ID}, "
            f"got {array.shape[1]}"
        )

    return array


def build_text_payload(record: StructuredRecord) -> tuple[list[str], list[str]]:
    labels: list[str] = []
    texts: list[str] = []

    for key in SECTION_KEYS:
        text = record.section_texts[key]
        if is_real_section_text(text):
            labels.append(key)
            texts.append(text)

    return labels, texts


def save_embedding_bundle(
    record: StructuredRecord,
    section_labels: list[str],
    embeddings: np.ndarray,
) -> Path:
    artifact = EmbeddingArtifact(
        doc_id=record.doc_id,
        route=record.route,
        section_labels=tuple(section_labels),
        embeddings=embeddings,
        source_path=str(record.source_path),
    )

    output_path = resolve_output_path(record)
    return artifact.write_npz(output_path)


def ensure_manifest_row(record: StructuredRecord) -> None:
    upsert_record(
        ManifestRecord(
            doc_id=record.doc_id,
            source_pdf_path="",
            source_filename=record.source_path.name,
            route=record.route,
            year="",
        )
    )


def process_record(
    json_path: Path,
    tokenizer: TokenizerProtocol,
    model: ModelProtocol,
) -> tuple[str, Path | None]:
    record = load_structured_record(json_path)
    ensure_manifest_row(record)

    section_labels, texts = build_text_payload(record)

    if not texts:
        print(f"[SKIP] {record.doc_id} contains no embeddable section text")
        return record.doc_id, None

    embeddings = embed_texts(texts=texts, tokenizer=tokenizer, model=model)

    if embeddings.shape[0] != len(section_labels):
        raise ValueError(
            f"Section-label count mismatch for {record.doc_id}: "
            f"{len(section_labels)} labels vs {embeddings.shape[0]} embeddings"
        )

    output_path = save_embedding_bundle(record, section_labels, embeddings)
    return record.doc_id, output_path


def main() -> None:
    tokenizer, model = load_model()
    json_files = list(iter_structured_json_files(STRUCTURED_DIR))

    if not json_files:
        raise FileNotFoundError(f"No structured JSON files found in {STRUCTURED_DIR}")

    print(f"Found {len(json_files)} structured JSON files.")

    success_count = 0
    skip_count = 0
    error_count = 0

    for index, json_path in enumerate(json_files, start=1):
        doc_id = ""

        try:
            doc_id, output_path = process_record(json_path, tokenizer, model)

            if output_path is None:
                skip_count += 1
                mark_stage_skipped(
                    doc_id,
                    "embedding_status",
                    "no embeddable section text",
                )
                print(f"[{index}/{len(json_files)}] skipped {json_path}")
                continue

            mark_stage_success(doc_id, "embedding_status")
            success_count += 1
            print(f"[{index}/{len(json_files)}] wrote {output_path}")

        except Exception as exc:
            error_count += 1
            if doc_id:
                mark_stage_failure(doc_id, "embedding_status", str(exc))
            print(f"[ERROR] [{index}/{len(json_files)}] {json_path}: {exc}")

    print(
        f"Embedding complete. Wrote {success_count} files, "
        f"skipped {skip_count}, errors {error_count}. "
        f"Output root: {EMBEDDINGS_DIR}"
    )


if __name__ == "__main__":
    main()