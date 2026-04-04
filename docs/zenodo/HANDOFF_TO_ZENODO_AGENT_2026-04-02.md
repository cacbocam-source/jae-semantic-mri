# Handoff to Zenodo Agent — Journal Corpus Audit Full Corpus Release

## Release identity

- Canonical analysis freeze commit: `71217d3`
- Public release-preparation lineage head: current `HEAD`
- Preferred public release tag: `checkpoint-full-corpus-nomic-content-only-2026-04-02-r3`

## Project identity

Repository: `jae-semantic-mri`

Public release title:
**Journal Corpus Audit: Full-Corpus Reconstruction and Semantic Analysis, 1960–2026**

## Contributor line

- Clemons, C. A.
- McKibben, J. D.
- Lindner, J. R.

## What this release contains

This release is the first full-corpus public package built from:

1. real `nomic-embed-text-v1.5` document embeddings
2. content-only article section extraction:
   - `A_intro`
   - `A_methods`
   - `A_results`
3. regenerated route-level metrics
4. regenerated APA outputs
5. explicit legacy-to-modern bridge analysis

## Core substantive feature

The release includes a dedicated bridge estimate for the key hinge transition:

- `1995-1999 -> 2000-2004`

This bridge is reported separately from route-internal innovation velocity.

## Canonical release artifacts

### Code
- `bins/s03_analysis/embedder.py`
- `bins/s06_analysis/bridge_analysis.py`

### Ledger and metrics
- `data/manifests/pipeline_manifest.csv`
- `data/metrics/Route_A_Modern/metrics.npz`
- `data/metrics/Route_B_Legacy/metrics.npz`

### Analysis tables
- `analysis_outputs/tables/Route_A_Modern_epoch_summary.csv`
- `analysis_outputs/tables/Route_A_Modern_innovation_velocity.csv`
- `analysis_outputs/tables/Route_B_Legacy_epoch_summary.csv`
- `analysis_outputs/tables/Route_B_Legacy_innovation_velocity.csv`
- `analysis_outputs/tables/bridge_transition_innovation_velocity.csv`

### Manuscript-facing tables
- `manuscript/paper/tables/Table_1_epoch_summary.md`
- `manuscript/paper/tables/Table_2_innovation_velocity.md`
- `manuscript/paper/tables/Table_3_bridge_transition.md`

### Manuscript-facing figure notes
- `manuscript/paper/figures/Figure_1_epoch_dispersion.md`
- `manuscript/paper/figures/Figure_2_innovation_velocity.md`
- `manuscript/paper/figures/Figure_3_bridge_transition.md`

## Zenodo metadata guidance

This repository now includes both:
- `.zenodo.json`
- `CITATION.cff`

For the GitHub→Zenodo release, `.zenodo.json` is the authoritative Zenodo metadata source.

## Recommended release description

Full Journal of Agricultural Education corpus (1960–2026) reconstructed and analyzed with real `nomic-embed-text-v1.5` document embeddings using content-only structured sections (`A_intro`, `A_methods`, `A_results`), route-level semantic dispersion and innovation-velocity metrics, APA-formatted outputs, and an explicit legacy-to-modern bridge transition analysis.

## Final Zenodo tasks

1. Create GitHub release from `checkpoint-full-corpus-nomic-content-only-2026-04-02-r3`
2. Verify Zenodo ingest
3. Capture:
   - GitHub release URL
   - Zenodo record URL
   - Version DOI
   - Concept DOI
4. Return those identifiers to the main workflow
