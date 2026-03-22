from __future__ import annotations

from dataclasses import dataclass
from typing import Final

A_TAK: Final[str] = "A_TAK"
A_INTRO: Final[str] = "A_intro"
A_METHODS: Final[str] = "A_methods"
A_RESULTS: Final[str] = "A_results"

SECTION_KEYS: Final[tuple[str, str, str, str]] = (
    A_TAK,
    A_INTRO,
    A_METHODS,
    A_RESULTS,
)

ROUTE_MODERN: Final[str] = "Route_A_Modern"
ROUTE_LEGACY: Final[str] = "Route_B_Legacy"

VALID_ROUTES: Final[frozenset[str]] = frozenset({
    ROUTE_MODERN,
    ROUTE_LEGACY,
})

SECTION_NOT_FOUND: Final[str] = "SECTION_NOT_FOUND"

EMBEDDING_BUNDLE_KEY_DOC_ID: Final[str] = "doc_id"
EMBEDDING_BUNDLE_KEY_ROUTE: Final[str] = "route"
EMBEDDING_BUNDLE_KEY_SECTION_LABELS: Final[str] = "section_labels"
EMBEDDING_BUNDLE_KEY_EMBEDDINGS: Final[str] = "embeddings"
EMBEDDING_BUNDLE_KEY_SOURCE_PATH: Final[str] = "source_path"

EMBEDDING_BUNDLE_REQUIRED_KEYS: Final[frozenset[str]] = frozenset({
    EMBEDDING_BUNDLE_KEY_DOC_ID,
    EMBEDDING_BUNDLE_KEY_ROUTE,
    EMBEDDING_BUNDLE_KEY_SECTION_LABELS,
    EMBEDDING_BUNDLE_KEY_EMBEDDINGS,
    EMBEDDING_BUNDLE_KEY_SOURCE_PATH,
})

@dataclass(frozen=True)
class StructuredSections:
    A_TAK: str
    A_intro: str
    A_methods: str
    A_results: str

    def as_dict(self) -> dict[str, str]:
        return {
            A_TAK: self.A_TAK,
            A_INTRO: self.A_intro,
            A_METHODS: self.A_methods,
            A_RESULTS: self.A_results,
        }