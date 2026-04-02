# Handoff to Zenodo Agent — Full Corpus Freeze

## Freeze identity

- Freeze commit: `71217d3`
- Preferred release tag: `checkpoint-full-corpus-nomic-content-only-2026-04-02-r1`
- Freeze date: 2026-04-02

## Project identity

Repository: `JAE_Legacy_Audit`

Study scope: full Journal of Agricultural Education corpus reconstructed across 1960–2026.

Route split:
- `Route_B_Legacy` = 1960–1999
- `Route_A_Modern` = 2000–2026

## What changed in this freeze

This freeze supersedes prior pseudo-valid rebuilds.

Critical methodological corrections:
1. Placeholder/random embedding generation was removed.
2. Real `nomic-ai/nomic-embed-text-v1.5` document embeddings are now used.
3. Embedding input is now content-only:
   - `A_intro`
   - `A_methods`
   - `A_results`
4. Route metrics were rebuilt from fresh embeddings.
5. APA outputs were rebuilt.
6. A legacy-to-modern bridge analysis was added for the key hinge transition:
   - `1995-1999 -> 2000-2004`

## Current analytic status

This is the first full-corpus freeze built from:
- real nomic embeddings
- content-only structured text extraction
- fresh route metrics
- explicit bridge transition analysis

## Key release artifacts

### Code
- `bins/s03_analysis/embedder.py`
- `bins/s06_analysis/bridge_analysis.py`

### Corpus ledger
- `data/manifests/pipeline_manifest.csv`

### Metrics
Live paths:
- `data/metrics/Route_A_Modern/metrics.npz`
- `data/metrics/Route_B_Legacy/metrics.npz`

Checkpoint copies committed for freeze stability:
- `checkpoints/2026-04-02_full_corpus_nomic_content_only_bridge/metrics.npz`
- `checkpoints/2026-04-02_full_corpus_nomic_content_only_bridge/pipeline_manifest.csv`

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

## Key substantive result for Zenodo/record description

The previously missing hinge transition is now quantified separately:

- Legacy-to-modern bridge transition:
  - `1995-1999 -> 2000-2004`
  - reported in `Table_3_bridge_transition.md`

This bridge value must be preserved in any release description and handoff narrative because it is central to the study’s deceleration argument.

## What the Zenodo agent should do

1. Verify the release tag exists:
   - `checkpoint-full-corpus-nomic-content-only-2026-04-02-r1`
2. Ensure the GitHub release is created from that tag.
3. Verify repository metadata source:
   - if both `.zenodo.json` and `CITATION.cff` exist, Zenodo will use `.zenodo.json`
4. Validate metadata before release:
   - creators
   - title
   - description
   - license
   - keywords
   - funding / related identifiers if needed
5. Archive the GitHub release into Zenodo.
6. After Zenodo ingest, inspect metadata and edit if needed.
7. Capture:
   - Zenodo DOI
   - concept DOI
   - record URL
   - release URL
8. Return those identifiers to the main workflow.

## Metadata note

Zenodo release metadata priority:
1. `.zenodo.json`
2. `CITATION.cff`
3. GitHub repository license / metadata fallback

If release ingestion fails, first inspect `.zenodo.json` and `CITATION.cff` validity.

## Recommended short repository description for Zenodo

Full Journal of Agricultural Education corpus (1960–2026) reconstructed and analyzed with real `nomic-embed-text-v1.5` document embeddings using content-only structured sections (`A_intro`, `A_methods`, `A_results`), route-level semantic dispersion and innovation-velocity metrics, APA-formatted outputs, and an explicit legacy-to-modern bridge transition analysis.
