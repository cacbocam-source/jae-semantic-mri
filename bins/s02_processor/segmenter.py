from __future__ import annotations

import re
from dataclasses import dataclass


SECTION_NOT_FOUND = "SECTION_NOT_FOUND"


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
    - A_Intro
    - A_Methods
    - A_Results
    """

    def __init__(self, text: str, year: int) -> None:
        self.text = text.strip() if text else ""
        self.year = int(year)

    def get_sections(self) -> dict[str, str]:
        """
        Return the canonical section mapping.
        """
        if not self.text:
            return self._empty_sections()

        if self.year < 1985:
            return self._segment_era_1()

        return self._segment_era_3()

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
            "A_TAK": SECTION_NOT_FOUND,
            "A_Intro": SECTION_NOT_FOUND,
            "A_Methods": SECTION_NOT_FOUND,
            "A_Results": SECTION_NOT_FOUND,
        }

    def _segment_era_1(self) -> dict[str, str]:
        """
        Proximity-based slicing for unstandardized legacy papers.

        This version is more robust for OCR-derived text by falling back to
        character-range slicing if line-based segmentation is too sparse.
        """
        lines = [line.strip() for line in self.text.splitlines() if line.strip()]

        if not lines:
            return self._empty_sections()

        # OCR text can collapse structure. Fall back to character windows if needed.
        if len(lines) < 30:
            text = self.text.strip()
            total_chars = len(text)

            if total_chars == 0:
                return self._empty_sections()

            tak_end = min(max(400, int(total_chars * 0.20)), total_chars)
            intro_end = min(max(tak_end, int(total_chars * 0.45)), total_chars)
            methods_end = min(max(intro_end, int(total_chars * 0.65)), total_chars)

            a_tak = text[:tak_end].strip()
            a_intro = text[tak_end:intro_end].strip()
            a_methods = text[intro_end:methods_end].strip()
            a_results = text[methods_end:].strip()

            return {
                "A_TAK": a_tak if a_tak else SECTION_NOT_FOUND,
                "A_Intro": a_intro if a_intro else SECTION_NOT_FOUND,
                "A_Methods": a_methods if a_methods else SECTION_NOT_FOUND,
                "A_Results": a_results if a_results else SECTION_NOT_FOUND,
            }

        total = len(lines)

        tak_end = min(15, total)
        intro_end = max(tak_end, int(total * 0.40))
        methods_end = max(intro_end, int(total * 0.60))

        a_tak = "\n".join(lines[:tak_end]).strip()
        a_intro = "\n".join(lines[tak_end:intro_end]).strip()
        a_methods = "\n".join(lines[intro_end:methods_end]).strip()
        a_results = "\n".join(lines[methods_end:]).strip()

        return {
            "A_TAK": a_tak if a_tak else SECTION_NOT_FOUND,
            "A_Intro": a_intro if a_intro else SECTION_NOT_FOUND,
            "A_Methods": a_methods if a_methods else SECTION_NOT_FOUND,
            "A_Results": a_results if a_results else SECTION_NOT_FOUND,
        }

    def _segment_era_3(self) -> dict[str, str]:
        """
        Regex-based slicing for standardized modern papers.
        """
        return {
            "A_TAK": self._regex_find(
                r"(?:Abstract)(.*?)(?:Introduction|Purpose|Theoretical Framework)",
                self.text,
            ),
            "A_Intro": self._regex_find(
                r"(?:Introduction|Theoretical Framework|Purpose and Research Questions)"
                r"(.*?)(?:Methodology|Methods)",
                self.text,
            ),
            "A_Methods": self._regex_find(
                r"(?:Methodology|Methods)(.*?)(?:Findings|Results|Discussion)",
                self.text,
            ),
            "A_Results": self._regex_find(
                r"(?:Findings|Results|Discussion)(.*?)$",
                self.text,
            ),
        }

    def _regex_find(self, pattern: str, text: str) -> str:
        """
        Return the first matched section body or SECTION_NOT_FOUND.
        """
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else SECTION_NOT_FOUND


if __name__ == "__main__":
    print("segmenter.py is a library module. Import it from the project root.")