from __future__ import annotations

from pathlib import Path

from config import RAW_DIR, STRUCTURED_DIR
from bins.s01_ingest.ledger import infer_route, make_doc_id
from bins.s02_processor.segmenter import UniversalSegmenter
from bins.s02_processor.smart_extract import smart_extract_pdf
from bins.s04_utils.artifacts import (
    StructuredSectionArtifact,
    build_structured_section_artifact,
)
from bins.s04_utils.year_resolution import resolve_year


def _route_a_prefixed_year(path: Path) -> int | None:
    stem = path.stem
    if len(stem) >= 4 and stem[:4].isdigit():
        return int(stem[:4])
    return None


def _resolve_section_year(path: Path) -> int:
    if infer_route(path) == "Route_A_Modern":
        prefixed_year = _route_a_prefixed_year(path)
        if prefixed_year is not None:
            return prefixed_year
    return resolve_year(path)


def build_section_export(pdf_path: str | Path) -> StructuredSectionArtifact:
    path = Path(pdf_path).expanduser().resolve()

    extraction = smart_extract_pdf(path)
    year = _resolve_section_year(path)

    segmenter = UniversalSegmenter(extraction.clean_text, year)
    segmentation = segmenter.get_result()

    return build_structured_section_artifact(
        doc_id=make_doc_id(path),
        source_filename=path.name,
        source_pdf_path=str(path),
        route=infer_route(path),
        year=year,
        extraction_method=extraction.method,
        page_count=extraction.page_count,
        raw_text_length=extraction.raw_text_length,
        clean_text_length=extraction.clean_text_length,
        segmentation_strategy=segmentation.strategy,
        sections=segmentation.sections,
    )


def structured_output_path(pdf_path: str | Path) -> Path:
    path = Path(pdf_path).expanduser().resolve()
    relative_path = path.relative_to(RAW_DIR)
    return (STRUCTURED_DIR / relative_path).with_suffix(".json")


def write_section_export(pdf_path: str | Path) -> Path:
    artifact = build_section_export(pdf_path)
    output_path = structured_output_path(pdf_path)
    return artifact.write_json(output_path)


if __name__ == "__main__":
    print("section_export.py is a library module. Import it from the project root.")
