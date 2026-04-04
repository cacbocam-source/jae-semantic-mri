# GitHub → Zenodo Release Checklist

## Git state
- [ ] Working tree is clean enough for release
- [ ] Canonical analysis freeze commit remains: `71217d3`
- [ ] Public release tag exists: `checkpoint-full-corpus-nomic-content-only-2026-04-02-r3`

## Metadata state
- [ ] `.zenodo.json` present
- [ ] `CITATION.cff` present
- [ ] Title matches public release title
- [ ] Contributor list matches:
  - Clemons, C. A.
  - McKibben, J. D.
  - Lindner, J. R.
- [ ] Description is correct
- [ ] Keywords are correct

## Release state
- [ ] Push `main`
- [ ] Push `checkpoint-full-corpus-nomic-content-only-2026-04-02-r3`
- [ ] Create GitHub release from r3 tag
- [ ] Verify Zenodo ingest
- [ ] Capture DOI, concept DOI, GitHub release URL, and Zenodo record URL
