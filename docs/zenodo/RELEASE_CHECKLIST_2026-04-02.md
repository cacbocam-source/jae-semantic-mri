# GitHub → Zenodo Release Checklist

## Git state
- [ ] Working tree is clean
- [ ] Freeze commit is present: `71217d3`
- [ ] Tag exists: `checkpoint-full-corpus-nomic-content-only-2026-04-02-r1`

## Metadata state
- [ ] Inspect whether `.zenodo.json` exists
- [ ] Inspect whether `CITATION.cff` exists
- [ ] If both exist, confirm `.zenodo.json` is authoritative
- [ ] Validate creators
- [ ] Validate title
- [ ] Validate license
- [ ] Validate description / abstract
- [ ] Validate related identifiers / grants if required

## Release state
- [ ] Create GitHub release from the final tag
- [ ] Ensure release notes mention:
  - real nomic embeddings
  - content-only input fields
  - bridge transition analysis
- [ ] Wait for Zenodo archive creation
- [ ] Inspect Zenodo metadata
- [ ] Edit Zenodo metadata if needed
- [ ] Record DOI, concept DOI, and Zenodo URL

## Final handoff
- [ ] Return DOI and concept DOI
- [ ] Return GitHub release URL
- [ ] Return Zenodo record URL
- [ ] Confirm archived version corresponds to commit `71217d3`
