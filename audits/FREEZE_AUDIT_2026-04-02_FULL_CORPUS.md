# Freeze Audit — 2026-04-02 Full Corpus Nomic + Bridge Rebuild

## Freeze identifiers

- Commit: `71217d3`
- Target tag: `checkpoint-full-corpus-nomic-content-only-2026-04-02-r1`

## Audit summary

This audit records the first full-corpus rebuild that satisfies all of the following:

- real `nomic-ai/nomic-embed-text-v1.5` embeddings
- content-only embedding input from:
  - `A_intro`
  - `A_methods`
  - `A_results`
- regenerated route metrics
- regenerated APA tables and figure notes
- explicit bridge transition analysis

## Prior failure modes corrected

1. Random placeholder embedder invalidated prior semantic results.
2. Whole-JSON serialization contaminated embedding inputs with metadata.
3. The route-internal innovation table omitted the cross-route hinge transition.

## Current corrected outputs

### Metrics
- `data/metrics/Route_A_Modern/metrics.npz`
- `data/metrics/Route_B_Legacy/metrics.npz`

### Route tables
- `analysis_outputs/tables/Route_A_Modern_epoch_summary.csv`
- `analysis_outputs/tables/Route_A_Modern_innovation_velocity.csv`
- `analysis_outputs/tables/Route_B_Legacy_epoch_summary.csv`
- `analysis_outputs/tables/Route_B_Legacy_innovation_velocity.csv`

### Bridge table
- `analysis_outputs/tables/bridge_transition_innovation_velocity.csv`

### Manuscript tables
- `manuscript/paper/tables/Table_1_epoch_summary.md`
- `manuscript/paper/tables/Table_2_innovation_velocity.md`
- `manuscript/paper/tables/Table_3_bridge_transition.md`

### Figure notes
- `manuscript/paper/figures/Figure_1_epoch_dispersion.md`
- `manuscript/paper/figures/Figure_2_innovation_velocity.md`
- `manuscript/paper/figures/Figure_3_bridge_transition.md`

## Hinge confirmation

The legacy-to-modern hinge is now explicitly represented as:
- `1995-1999 -> 2000-2004`

This value is stored separately from the route-internal innovation table and must be treated as part of the canonical freeze.

## Freeze recommendation

This freeze should be treated as the stable release candidate for GitHub→Zenodo archiving, pending metadata validation and release creation from the final tag.
