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
    - Era 3: post-1984 documents using heading-driven segmentation (>= 1985)

    Canonical output sections:
    - A_TAK
    - A_intro
    - A_methods
    - A_results
    """

    ERA3_ABSTRACT_HEADS = [
        r"abstract",
    ]

    ERA3_INTRO_HEADS = [
        r"[i1l]ntroduction",
        r"purpose(?:\s+of\s+the\s+study)?",
        r"purpose\s+and\s+objectives?",
        r"purpose\s+and\s+objective",
        r"purpose\s+and\s+research\s+questions?",
        r"objectives?",
        r"problem",
        r"statement\s+of\s+the\s+problem",
        r"background",
        r"theoretical\s+framework",
        r"need\s+for\s+the\s+study",
    ]

    ERA3_METHODS_HEADS = [
        r"method(?:ology)?",
        r"methods?",
        r"procedures?",
        r"procedures?\s+and\s+analysis",
        r"statistical\s+procedures?",
        r"research\s+design",
        r"design",
        r"population",
        r"sample",
        r"instrumentation",
        r"data\s+collection",
        r"analysis\s+of\s+data",
        r"data\s+analysis",
        r"delphi",
    ]

    ERA3_RESULTS_HEADS = [
        r"findings",
        r"major\s+findings",
        r"descriptive\s+results",
        r"results?",
        r"summary",
        r"discussion",
    ]

    ERA3_TAIL_HEADS = [
        r"conclusions?",
        r"conclusions?\s+and\s+recommendations?",
        r"recommendations?",
        r"other\s+considerations",
        r"implications?",
        r"references?",
        r"literature\s+cited",
        r"acknowledg(?:e)?ments?",
    ]

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
        Heading-driven slicing for post-1984 papers.

        This branch supports both standardized modern headings and
        legacy APA-style topical Level 1 headings used in OCR-era files.
        """
        abstract_span = self._find_heading_span(self.ERA3_ABSTRACT_HEADS)
        intro_span = self._find_heading_span(self.ERA3_INTRO_HEADS)
        methods_span = self._find_heading_span(self.ERA3_METHODS_HEADS)
        results_span = self._find_heading_span(self.ERA3_RESULTS_HEADS)
        tail_span = self._find_heading_span(self.ERA3_TAIL_HEADS)

        a_tak = SECTION_NOT_FOUND
        if abstract_span is not None:
            a_tak = self._slice_section(
                abstract_span[1],
                self._next_heading_start(
                    abstract_span[1],
                    intro_span,
                    methods_span,
                    results_span,
                    tail_span,
                ),
            )

        a_intro = SECTION_NOT_FOUND
        if intro_span is not None:
            a_intro = self._slice_section(
                intro_span[1],
                self._next_heading_start(
                    intro_span[1],
                    methods_span,
                    results_span,
                    tail_span,
                ),
            )
        else:
            intro_fallback_start = abstract_span[1] if abstract_span is not None else self._approximate_body_start()
            intro_fallback_end = self._next_heading_start(
                intro_fallback_start,
                methods_span,
                results_span,
                tail_span,
            )
            if intro_fallback_end is not None and intro_fallback_end > intro_fallback_start:
                candidate = self._slice_section(intro_fallback_start, intro_fallback_end)
                if candidate != SECTION_NOT_FOUND and len(candidate) >= 100:
                    a_intro = candidate

        a_methods = SECTION_NOT_FOUND
        if methods_span is not None:
            a_methods = self._slice_section(
                methods_span[1],
                self._next_heading_start(
                    methods_span[1],
                    results_span,
                    tail_span,
                ),
            )

        if a_methods == SECTION_NOT_FOUND and a_intro != SECTION_NOT_FOUND:
            recovered = self._recover_methods_from_intro(a_intro)
            if recovered is not None:
                a_intro, a_methods = recovered

        a_results = SECTION_NOT_FOUND
        if results_span is not None:
            a_results = self._slice_section(
                results_span[1],
                self._next_heading_start(
                    results_span[1],
                    tail_span,
                ),
            )

        if a_methods == SECTION_NOT_FOUND and a_results != SECTION_NOT_FOUND:
            recovered = self._recover_methods_from_results_prefix(a_results)
            if recovered is not None:
                a_methods, a_results = recovered

        if a_methods != SECTION_NOT_FOUND and a_results != SECTION_NOT_FOUND:
            a_methods, a_results = self._cleanup_methods_results_boundary(a_methods, a_results)

        return {
            A_TAK: a_tak,
            A_INTRO: a_intro,
            A_METHODS: a_methods,
            A_RESULTS: a_results,
        }

    def _approximate_body_start(self) -> int:
        lines = self.text.splitlines(keepends=True)
        consumed = 0
        nonempty = 0
        for line in lines:
            consumed += len(line)
            if line.strip():
                nonempty += 1
            if nonempty >= 8:
                break
        return min(consumed, 1200)

    def _recover_methods_from_intro(self, intro_text: str) -> tuple[str, str] | None:
        if not intro_text or intro_text == SECTION_NOT_FOUND:
            return None

        text = intro_text.strip()
        if len(text) < 400:
            return None

        patterns = [
            r"(?im)^\s*procedures?\s+and\s+analysis\s*:?",
            r"(?im)^\s*procedures?\s*:?",
            r"(?im)^\s*statistical\s+procedures?\s*:?",
            r"(?im)^\s*research\s+design\s*:?",
            r"(?im)^\s*population\s*:?",
            r"(?im)^\s*sample\s*:?",
            r"(?im)^\s*instrumentation\s*:?",
            r"(?im)^\s*data\s+collection\s*:?",
            r"(?im)^\s*analysis\s+of\s+data\s*:?",
            r"(?im)^\s*data\s+analysis\s*:?",
            r"(?im)^\s*delphi\s*:?",
            r"(?i)\bthis study was designed\b",
            r"(?i)\bthis study used\b",
            r"(?i)\bthe population consisted\b",
            r"(?i)\bthe sample consisted\b",
            r"(?i)\bthe investigation was conducted\b",
            r"(?i)\bdata were analyzed\b",
            r"(?i)\bdata were collected\b",
            r"(?i)\bthe research design\b",
            r"(?i)\bquestionnaire\b",
            r"(?i)\binstrument(?:ation)?\b",
            r"(?i)\brespondents?\b",
        ]

        best_start = None
        min_start = max(120, int(len(text) * 0.08))

        for pattern in patterns:
            m = re.search(pattern, text)
            if not m:
                continue
            if m.start() < min_start:
                continue
            if best_start is None or m.start() < best_start:
                best_start = m.start()

        if best_start is None:
            return None

        intro_part = text[:best_start].strip()
        methods_part = text[best_start:].strip()

        if len(intro_part) < 100 or len(methods_part) < 100:
            return None

        return (
            normalize_section_text(intro_part),
            normalize_section_text(methods_part),
        )

    def _recover_methods_from_results_prefix(self, results_text: str) -> tuple[str, str] | None:
        if not results_text or results_text == SECTION_NOT_FOUND:
            return None

        text = results_text.strip()
        if len(text) < 500:
            return None

        methods_markers = [
            r"(?im)^\s*procedures?\s+and\s+analysis\s*:?",
            r"(?im)^\s*procedures?\s*:?",
            r"(?im)^\s*research\s+design\s*:?",
            r"(?im)^\s*population\s*:?",
            r"(?im)^\s*sample\s*:?",
            r"(?im)^\s*instrumentation\s*:?",
            r"(?im)^\s*data\s+collection\s*:?",
            r"(?im)^\s*analysis\s+of\s+data\s*:?",
            r"(?im)^\s*data\s+analysis\s*:?",
            r"(?i)\bthe population consisted\b",
            r"(?i)\bdata were collected\b",
            r"(?i)\bquestionnaire\b",
        ]

        results_markers = [
            r"(?im)^\s*results?\s*:?",
            r"(?im)^\s*findings\s*:?",
            r"(?im)^\s*major\s+findings\s*:?",
            r"(?im)^\s*descriptive\s+results\s*:?",
            r"(?im)^\s*enrollment\s+data\s*:?",
            r"(?im)^\s*discussion\s*:?",
        ]

        method_start = None
        for pattern in methods_markers:
            m = re.search(pattern, text)
            if m:
                if method_start is None or m.start() < method_start:
                    method_start = m.start()

        if method_start is None:
            return None

        result_start = None
        for pattern in results_markers:
            m = re.search(pattern, text[method_start + 50 :])
            if m:
                candidate = method_start + 50 + m.start()
                if result_start is None or candidate < result_start:
                    result_start = candidate

        if result_start is None:
            return None

        methods_part = text[method_start:result_start].strip()
        results_part = text[result_start:].strip()

        if len(methods_part) < 100 or len(results_part) < 100:
            return None

        return (
            normalize_section_text(methods_part),
            normalize_section_text(results_part),
        )

    def _cleanup_methods_results_boundary(self, methods_text: str, results_text: str) -> tuple[str, str]:
        if (
            not methods_text or methods_text == SECTION_NOT_FOUND
            or not results_text or results_text == SECTION_NOT_FOUND
        ):
            return methods_text, results_text

        text = results_text.strip()
        if len(text) < 300:
            return methods_text, results_text

        method_markers = [
            r"(?im)^\s*procedures?\s+and\s+analysis\s*:?",
            r"(?im)^\s*procedures?\s*:?",
            r"(?im)^\s*research\s+design\s*:?",
            r"(?im)^\s*population\s*:?",
            r"(?im)^\s*sample\s*:?",
            r"(?im)^\s*instrumentation\s*:?",
            r"(?im)^\s*data\s+collection\s*:?",
            r"(?im)^\s*analysis\s+of\s+data\s*:?",
            r"(?im)^\s*data\s+analysis\s*:?",
            r"(?i)\bthe population consisted\b",
            r"(?i)\bdata were collected\b",
            r"(?i)\bquestionnaire\b",
        ]

        results_markers = [
            r"(?im)^\s*results?\s*:?",
            r"(?im)^\s*findings\s*:?",
            r"(?im)^\s*major\s+findings\s*:?",
            r"(?im)^\s*descriptive\s+results\s*:?",
            r"(?im)^\s*enrollment\s+data\s*:?",
            r"(?im)^\s*discussion\s*:?",
        ]

        leading_method_start = None
        for pattern in method_markers:
            m = re.search(pattern, text)
            if m and m.start() <= 120:
                if leading_method_start is None or m.start() < leading_method_start:
                    leading_method_start = m.start()

        if leading_method_start is None:
            return methods_text, results_text

        result_start = None
        search_text = text[leading_method_start + 50 :]
        for pattern in results_markers:
            m = re.search(pattern, search_text)
            if m:
                candidate = leading_method_start + 50 + m.start()
                if result_start is None or candidate < result_start:
                    result_start = candidate

        if result_start is None:
            return methods_text, results_text

        moved_methods = text[leading_method_start:result_start].strip()
        cleaned_results = text[result_start:].strip()

        if len(moved_methods) < 100 or len(cleaned_results) < 100:
            return methods_text, results_text

        merged_methods = normalize_section_text((methods_text + "\n\n" + moved_methods).strip())
        cleaned_results = normalize_section_text(cleaned_results)
        return merged_methods, cleaned_results

    def _find_heading_span(self, headings: list[str]) -> tuple[int, int] | None:
        """
        Return the earliest matching heading span for a list of heading variants.
        """
        matches: list[tuple[int, int]] = []
        for heading in headings:
            pattern = rf"(?im)^\s*(?:\d+[\.\)])?\s*{heading}\s*:?\s*$"
            match = re.search(pattern, self.text)
            if match:
                matches.append((match.start(), match.end()))

        if not matches:
            return None

        return sorted(matches, key=lambda x: x[0])[0]

    def _next_heading_start(self, after_pos: int, *spans: tuple[int, int] | None) -> int | None:
        starts = [span[0] for span in spans if span is not None and span[0] > after_pos]
        if not starts:
            return None
        return min(starts)

    def _slice_section(self, start: int, end: int | None) -> str:
        chunk = self.text[start:end].strip() if end is not None else self.text[start:].strip()
        if not chunk:
            return SECTION_NOT_FOUND
        return normalize_section_text(chunk)

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
