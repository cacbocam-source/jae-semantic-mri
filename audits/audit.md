

# Audit Log

## 2026-04-06 legacy corrective lane entry

- Scope: Route_B_Legacy OCR-era defect only
- Goal: determine and patch the section-localization / section-recovery failure in 1985–1994
- Evidence from fix-point audit:
  - failure cluster is overwhelmingly `ocr + era_3`
  - dominant patterns are:
    - A_intro missing, A_results present
    - A_intro missing, A_methods missing, A_results present
- Working hypothesis:
  - raw OCR text acquisition is partially functional
  - legacy `era_3` section anchoring is too rigid for legacy APA-style Level 1 headings
- Proposed first corrective experiment:
  - fuzzy legacy header matching
  - early-document header hunting
  - no broad OCR rewrite yet
- Expected fix point:
  - bins/s02_processor/segmenter.py -> _segment_era_3()

## 2026-04-06 legacy corrective lane — negative-result checkpoint

- Experiment: first `era_3` corrective patch in `bins/s02_processor/segmenter.py`
- Patch type:
  - widened legacy header lexicon
  - early-document intro fallback
- Rerun scope:
  - Route_B_Legacy control window: 1975–1984
  - Route_B_Legacy audit window: 1985–1994
- Operational result:
  - structured_ok = 583
  - structured_fail = 0
  - embed_ok = 583
  - embed_fail = 0
  - Route_B metrics rebuild completed on full route rows
  - Track A and Track B reran successfully
- Evaluation:
  - no material improvement in the OCR artifact surface
  - `section_not_found_rate` in the audit window remained 0.9223
  - Track A determination remained `ARTIFACT`
- Interpretation:
  - the first `era_3` header-lexicon / early-intro patch did not fix the legacy defect
  - the defect remains a section-localization / section-recovery failure
  - next lane should test a stronger second-stage corrective hypothesis rather than pushing
- Decision:
  - checkpoint as negative-result experiment
  - do not push to GitHub

## 2026-04-06 legacy corrective lane — second-stage patch started

- Basis:
  - first era_3 corrective patch produced a negative-result aggregate outcome
  - manual inspection of remaining failures showed two-column but readable PDFs
  - remaining failures split into:
    - all-three-missing collapse
    - partial anchor-miss cases
- Updated hypothesis:
  - partial failures still need stronger legacy heading normalization
  - no-introduction/no-abstract papers need stronger early-body intro fallback
- Immediate patch:
  - expand legacy era_3 heading lexicon further
  - add approximate early-body start fallback when no abstract/introduction heading exists
- Push status:
  - still do not push

## 2026-04-07 legacy corrective lane — positive-result freeze checkpoint

- Corrective status:
  - legacy section-localization / methods-recovery work produced a material reduction in the OCR artifact surface
  - audit-window `section_not_found_rate` improved to 0.2359 from earlier higher states
- Boundary-quality audit result:
  - methods-boundary residual is now small and heterogeneous
  - sampled residual subgroup counts:
    - target_count = 15
    - methods_missing_count = 2
    - results_prefix_method_marker_count = 3
    - methods_intro_like_count = 0
    - all_three_missing_count = 1
- Interpretation:
  - remaining residual is split across:
    - one hard total-collapse / likely layout case
    - one likely genre/non-empirical case
    - a very small methods/results boundary-noise subgroup
  - additional broad code patching in this lane is no longer justified
- Decision:
  - freeze the current legacy corrective code state
  - regenerate exports from the corrected Route_B state
  - document remaining residual as bounded rather than continuing exploratory patching
- Push status:
  - not yet pushing in this block
