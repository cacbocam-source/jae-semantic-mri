> Role: Operational acquisition runbook
> Authority: Subordinate to `AUDIT_CONTEXT.md`.
> Update rule: Use for acquisition procedure and intake logging; when it conflicts with `AUDIT_CONTEXT.md`, the audit context controls.


# Acquisition Log — Route_A_Modern

Status: Current Tier 00 operational acquisition-state/control surface  
Current-state authority: `AUDIT_CONTEXT.md`  
Chronology: `RESEARCH_LOG.md`

---

## Current validated admitted modern corpus

Current admitted modern source PDFs: **10**

Realized year coverage in the live admitted modern corpus:
- 2000
- 2001
- 2003
- 2007
- 2012
- 2013
- 2018
- 2022
- 2024
- 2026

Operational consequence:
- `Route_A_Modern` is no longer a singleton placeholder route
- Route A currently resolves into **6 epochs**
- Route A currently contributes **5 adjacent-epoch innovation-velocity transitions**
- modern closeout for 2000–2026 remains **deferred**, because live modern coverage is widened but not complete

---

## Accepted live raw-storage forms

Validated live modern raw layouts:

```text
data/raw/Route_A_Modern/<YEAR>.pdf
data/raw/Route_A_Modern/<YEAR>/<filename>.pdf
```

Validated examples:
- `data/raw/Route_A_Modern/2026.pdf -> 2026`
- `data/raw/Route_A_Modern/2024/10.5032_jae.v65i4.2828.pdf -> 2024`

---

## Year-resolution control rule

Resolution precedence for modern files:
1. manifest year when available
2. supported filename parsing
3. supported parent-directory parsing for admitted year-bucket modern files
4. fail fast if unresolved

Operational rule:
- unsupported filenames must not silently guess a year
- DOI-style filenames without an embedded year are valid only when stored under a year-bucket directory whose parent name is itself a valid year

---

## Controlled modern intake protocol

1. Acquire PDFs only; do not treat HTML or abstract metadata as corpus substitutes.
2. Stage and QC incoming files before promotion.
3. Promote validated files into canonical raw storage under one of the accepted live modern layouts.
4. Ensure each admitted file maps to exactly one route and one year.
5. Bridge promoted files into `data/manifests/pipeline_manifest.csv` using the canonical pipeline `doc_id` contract derived from the source PDF path.
6. Run downstream processing and analysis only after manifest integration is clean.
7. Regenerate route-level metrics artifacts and Phase 6 outputs after corpus expansion.
8. Synchronize current-state, methods, schema, and supplementary audit surfaces after validated expansion.

---

## Downstream rebuild sequence after modern intake

```bash
python3 main.py --phase process
python3 main.py --phase analyze
python3 bins/s03_analysis/metrics.py
python3 bins/s06_analysis/report_builder.py
python3 bins/s06_analysis/figure_builder.py
python3 bins/s06_analysis/apa_table_builder.py
python3 bins/s06_analysis/apa_figure_builder.py
```

Generated output surfaces affected by widened intake:
- `analysis_outputs/summaries/`
- `analysis_outputs/tables/`
- `analysis_outputs/figures/`
- `manuscript/paper/tables/`
- `manuscript/paper/figures/`

---

## Guardrails

- one source PDF = one document identity
- `doc_id` must derive from the source PDF path
- manifest integration and analysis execution must use the same `doc_id` contract
- parent-directory parsing is supported for admitted year-bucket modern files
- unresolved year cases must fail fast rather than guess
- generated documentation surfaces must not be manually edited at their fixed builder paths

---

## Current next-step boundary

The next correct work surface is not a false modern-complete closeout memo. It is:
- continued controlled corpus expansion where needed
- Phase 6 output/documentation synchronization
- restrained interpretive refinement within the validated descriptive boundary
- legacy-decade expansion without reopening stabilized engineering work unless contradictory evidence appears
