from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from config import RAW_DIR, STRUCTURED_DIR
from bins.s01_ingest.ledger import infer_route, make_doc_id
from bins.s02_processor.segmenter import UniversalSegmenter
from bins.s02_processor.smart_extract import smart_extract_pdf


@dataclass(frozen=True)
class SectionExport:
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
    sections: dict[str, str]


def infer_year_from_path(pdf_path: Path) -> int:
    """
    Infer year from filename for current benchmark-compatible workflow.
    """
    name = pdf_path.name

    if name == "2026.pdf":
        return 2026

    if name == "Vol1_1.pdf":
        return 1960

    stem = pdf_path.stem
    try:
        return int(stem)
    except ValueError as exc:
        raise ValueError(f"Unable to infer year from filename: {name}") from exc


def build_section_export(pdf_path: str | Path) -> SectionExport:
    path = Path(pdf_path).expanduser().resolve()

    extraction = smart_extract_pdf(path)
    year = infer_year_from_path(path)

    segmenter = UniversalSegmenter(extraction.clean_text, year)
    segmentation = segmenter.get_result()

    return SectionExport(
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
    export = build_section_export(pdf_path)
    output_path = structured_output_path(pdf_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(export), f, indent=2, ensure_ascii=False)

    return output_path


if __name__ == "__main__":
    print("section_export.py is a library module. Import it from the project root.")