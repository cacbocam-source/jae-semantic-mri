from __future__ import annotations

import re
from dataclasses import dataclass

from bins.s04_utils.schemas import (
    A_INTRO,
    A_METHODS,
    A_RESULTS,
    A_TAK,
    SECTION_NOT_FOUND,
)
from bins.s04_utils.validators import normalize_section_text, validate_section_mapping


@dataclass(frozen=True)
class SegmentationResult:
    """
    Structured segmentation output for a cleaned article text.
    """
    year: int
    strategy: str
    sections: dict[str, str]


class UniversalSegmenter:
    """
    Era-aware segmenter for Agricultural Education corpus documents.

    Routing:
    - Era 1: legacy, less standardized documents (< 1985)
    - Era 3: modern, standardized documents (>= 1985)

    Canonical output sections:
    - A_TAK
    - A_intro
    - A_methods
    - A_results
    """

    def __init__(self, text: str, year: int) -> None:
        self.text = text.strip() if text else ""
        self.year = int(year)

    def get_sections(self) -> dict[str, str]:
        """
        Return the canonical validated section mapping.
        """
        if not self.text:
            return self._empty_sections()

        if self.year < 1985:
            sections = self._segment_era_1()
        else:
            sections = self._segment_era_3()

        return validate_section_mapping(sections)

    def get_result(self) -> SegmentationResult:
        """
        Return a structured segmentation result with strategy metadata.
        """
        strategy = "era_1" if self.year < 1985 else "era_3"
        return SegmentationResult(
            year=self.year,
            strategy=strategy,
            sections=self.get_sections(),
        )

    def _empty_sections(self) -> dict[str, str]:
        return {
            A_TAK: SECTION_NOT_FOUND,
            A_INTRO: SECTION_NOT_FOUND,
            A_METHODS: SECTION_NOT_FOUND,
            A_RESULTS: SECTION_NOT_FOUND,
        }

    def _segment_era_1(self) -> dict[str, str]:
        """
        Proximity-based slicing for unstandardized legacy papers.

        For sparse OCR output, fall back to character-range slicing.
        For denser text, use line-based proportional slicing.
        """
        lines = [line.strip() for line in self.text.splitlines() if line.strip()]

        if not lines:
            return self._empty_sections()

        if len(lines) < 30:
            return self._segment_era_1_character_windows()

        return self._segment_era_1_line_windows(lines)

    def _segment_era_1_character_windows(self) -> dict[str, str]:
        text = self.text.strip()
        total_chars = len(text)

        if total_chars == 0:
            return self._empty_sections()

        tak_end = min(max(400, int(total_chars * 0.20)), total_chars)
        intro_end = min(max(tak_end, int(total_chars * 0.45)), total_chars)
        methods_end = min(max(intro_end, int(total_chars * 0.65)), total_chars)

        a_tak = text[:tak_end]
        a_intro = text[tak_end:intro_end]
        a_methods = text[intro_end:methods_end]
        a_results = text[methods_end:]

        return {
            A_TAK: normalize_section_text(a_tak),
            A_INTRO: normalize_section_text(a_intro),
            A_METHODS: normalize_section_text(a_methods),
            A_RESULTS: normalize_section_text(a_results),
        }

    def _segment_era_1_line_windows(self, lines: list[str]) -> dict[str, str]:
        total = len(lines)

        tak_end = min(15, total)
        intro_end = max(tak_end, int(total * 0.40))
        methods_end = max(intro_end, int(total * 0.60))

        a_tak = "\n".join(lines[:tak_end])
        a_intro = "\n".join(lines[tak_end:intro_end])
        a_methods = "\n".join(lines[intro_end:methods_end])
        a_results = "\n".join(lines[methods_end:])

        return {
            A_TAK: normalize_section_text(a_tak),
            A_INTRO: normalize_section_text(a_intro),
            A_METHODS: normalize_section_text(a_methods),
            A_RESULTS: normalize_section_text(a_results),
        }

    def _segment_era_3(self) -> dict[str, str]:
        """
        Regex-based slicing for standardized modern papers.
        """
        return {
            A_TAK: self._regex_find(
                r"(?:Abstract)\s*(.*?)(?:Introduction|Purpose|Theoretical Framework|Purpose and Research Questions)",
                self.text,
            ),
            A_INTRO: self._regex_find(
                r"(?:Introduction|Theoretical Framework|Purpose and Research Questions)\s*(.*?)(?:Methodology|Methods)",
                self.text,
            ),
            A_METHODS: self._regex_find(
                r"(?:Methodology|Methods)\s*(.*?)(?:Findings|Results|Discussion)",
                self.text,
            ),
            A_RESULTS: self._regex_find(
                r"(?:Findings|Results|Discussion)\s*(.*?)$",
                self.text,
            ),
        }

    def _regex_find(self, pattern: str, text: str) -> str:
        """
        Return the first matched section body or SECTION_NOT_FOUND.
        """
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if not match:
            return SECTION_NOT_FOUND

        return normalize_section_text(match.group(1))


if __name__ == "__main__":
    print("segmenter.py is a library module. Import it from the project root.")