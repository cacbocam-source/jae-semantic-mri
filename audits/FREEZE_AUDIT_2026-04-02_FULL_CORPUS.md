# Freeze Audit — Journal Corpus Audit Full-Corpus Release

## Core identities

- Canonical analysis freeze commit: `71217d3`
- Public release tag target: `checkpoint-full-corpus-nomic-content-only-2026-04-02-r4`

## Audit summary

This release package preserves the first full-corpus rebuild that satisfies all of the following:

- real `nomic-ai/nomic-embed-text-v1.5` embeddings
- content-only embedding input from:
  - `A_intro`
  - `A_methods`
  - `A_results`
- regenerated route metrics
- regenerated APA tables and figure notes
- explicit bridge transition analysis

## Key outputs

- `data/metrics/Route_A_Modern/metrics.npz`
- `data/metrics/Route_B_Legacy/metrics.npz`
- `analysis_outputs/tables/bridge_transition_innovation_velocity.csv`
- `manuscript/paper/tables/Table_3_bridge_transition.md`
- `manuscript/paper/figures/Figure_3_bridge_transition.md`

## Hinge confirmation

The legacy-to-modern hinge is explicitly represented as:

- `1995-1999 -> 2000-2004`

## Release recommendation

Treat this release as the public DOI-bearing package for the corrected full-corpus Journal Corpus Audit.
