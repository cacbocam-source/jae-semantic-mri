# Legacy Acquisition Build Report

## Scope
This build completes the acquisition-side architecture needed to move from metadata harvest to canonical manuscript intake under the current JAE_Legacy_Audit workflow.

## Deliverables
- `jae_legacy_acquisition_contract.py`
- `jae_openalex_prefill_builder_v2.py`
- `jae_prefill_downloader.py`
- `jae_prefill_promoter.py`
- `jae_prefill_manifest_bridge.py`
- `LEGACY_ACQUISITION_FULL_BUILD_WALKTHROUGH.md`
- `AUDIT_CONTEXT_20260320_LEGACY_ACQ_UPDATED.md`
- `RESEARCH_LOG_20260320_LEGACY_ACQ_UPDATED.md`

## Design choices
- The build is intentionally standalone and does not modify the stabilized load-bearing utility layer.
- Route assignment remains year-driven using `LEGACY_CUTOFF=2000`.
- Manuscript storage remains canonical under `data/raw_pdfs/<route>/<year>/`.
- Acquisition remains staging-first, then promotion, then manifest integration.
- Metadata/abstract harvesting is treated as acquisition support, not as the study dataset.

## Validation completed here
The Python acquisition scripts were syntax-checked with:

```bash
python3 -m py_compile   jae_legacy_acquisition_contract.py   jae_openalex_prefill_builder_v2.py   jae_prefill_downloader.py   jae_prefill_promoter.py   jae_prefill_manifest_bridge.py
```

No live network execution was performed in this environment.

## Operational boundary
This build extends the acquisition layer only. It does not replace or redesign:
- extraction
- structured export
- embeddings
- Phase 5 metrics
- post-Phase-5 validation

Those remain the stabilized downstream engine.

# Legacy Acquisition Build Report

## Scope
This build completes the acquisition-side architecture needed to move from metadata harvest to canonical manuscript intake under the current JAE_Legacy_Audit workflow.

## Deliverables
- `jae_legacy_acquisition_contract.py`
- `jae_openalex_prefill_builder_v2.py`
- `jae_prefill_downloader.py`
- `jae_prefill_promoter.py`
- `jae_prefill_manifest_bridge.py`
- `LEGACY_ACQUISITION_FULL_BUILD_WALKTHROUGH.md`
- `AUDIT_CONTEXT_20260320_LEGACY_ACQ_UPDATED.md`
- `RESEARCH_LOG_20260320_LEGACY_ACQ_UPDATED.md`

## Design choices
- The build is intentionally standalone and does not modify the stabilized load-bearing utility layer.
- Route assignment remains year-driven using `LEGACY_CUTOFF=2000`.
- The executed 1960–1969 batch was promoted into the live corpus under `data/raw/<route>/<year>/`; earlier `data/raw_pdfs/` references are historical/protocol planning residue.
- Acquisition remains staging-first, then promotion, then manifest integration.
- Metadata/abstract harvesting is treated as acquisition support, not as the study dataset.

## Validation completed here
The Python acquisition scripts were syntax-checked with:

```bash
python3 -m py_compile   jae_legacy_acquisition_contract.py   jae_openalex_prefill_builder_v2.py   jae_prefill_downloader.py   jae_prefill_promoter.py   jae_prefill_manifest_bridge.py
```

No live network execution was performed in the build environment itself.

Post-build execution milestone now verified separately:
- 1960–1969 legacy batch executed successfully
- 149 legacy PDFs downloaded into staging
- 149 legacy PDFs promoted into `data/raw/Route_B_Legacy/<year>/`
- 149 manifest rows added via the manifest bridge

## Operational boundary
This build extends the acquisition layer only. It does not replace or redesign:
- extraction
- structured export
- embeddings
- Phase 5 metrics
- post-Phase-5 validation

Those remain the stabilized downstream engine.


## Current active code path
The live acquisition code is currently operating from the repo-root path:

```text
legacy_acquisition/
```

rather than from `scripts/legacy_acquisition/`.
