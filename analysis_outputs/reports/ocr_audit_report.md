# Phase 6 Track A — OCR Audit Report

## Scope

- Route: Route_B_Legacy
- Control window: 1975-1984
- Audit window: 1985-1994
- Documents analyzed: 583
- SECTION_NOT_FOUND sentinel: SECTION_NOT_FOUND
- Short-document threshold: 200 characters

## Window summary

- audit_1985_1994: n=373, mean_combined_text_length=11985.3003, section_not_found_rate=0.2359, short_document_rate=0.0751, mean_ttr=0.2872, mean_non_ascii_rate=0.0009, mean_digit_alpha_ratio=0.0532
- control_1975_1984: n=210, mean_combined_text_length=12224.3571, section_not_found_rate=0.0000, short_document_rate=0.0000, mean_ttr=0.3057, mean_non_ascii_rate=0.0015, mean_digit_alpha_ratio=0.0349

## Audit-minus-control deltas

- mean_combined_text_length delta = -239.0569
- section_not_found_rate delta = 0.2359
- short_document_rate delta = 0.0751
- mean_ttr delta = -0.0186
- mean_non_ascii_rate delta = -0.0006
- mean_digit_alpha_ratio delta = 0.0182

## Highest-risk years

- 1986: section_not_found_rate=0.4000, short_document_rate=0.1429, mean_combined_text_length=9746.6286
- 1989: section_not_found_rate=0.3235, short_document_rate=0.0588, mean_combined_text_length=12974.6765
- 1991: section_not_found_rate=0.3143, short_document_rate=0.1143, mean_combined_text_length=11331.6286
- 1987: section_not_found_rate=0.2941, short_document_rate=0.0882, mean_combined_text_length=11406.5294
- 1993: section_not_found_rate=0.2500, short_document_rate=0.0909, mean_combined_text_length=12914.7273

## Determination

- ARTIFACT
- One or more explicit artifact criteria from the engineering brief were triggered.

## Rule binding

- Triggered artifact criteria:
  - SECTION_NOT_FOUND rate in 1985–1994 is > 0 while the control-window rate is 0.0, which satisfies the ≥2× control artifact criterion.

- ±20% signal checks:
  - mean_combined_text_length: PASS
  - section_not_found_rate: FAIL
  - short_document_rate: FAIL
  - mean_ttr: PASS
  - mean_non_ascii_rate: FAIL
  - mean_digit_alpha_ratio: FAIL

## Manuscript note

- The 1985–1994 velocity anomaly should be discussed as likely contaminated by OCR/section-extraction artifact.
- The epoch remains in the pipeline; this audit is diagnostic, not corrective.
