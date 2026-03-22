# Research Compliance

Version: 2.2
Date: 2026-03-20
Status: Supplemental compliance reference aligned to the stabilized Phase 5 state and the active beta pilot epoch protocol

---

# 1. Purpose

Core priorities:
- lawful data access
- respect for publisher and repository terms
- conservative network behavior
- reproducible processing
- auditable artifact generation
- clear separation of benchmark corpus, beta pilot corpus, and testing corpora

---

# 2. Current Operational Scope

Current implemented workflow covers:
- local corpus processing
- extraction and cleaning
- segmentation and structured export
- section embedding generation
- route-level metrics computation

Defined and authorized next:
- beta pilot live-manuscript intake under `data/raw_pdfs/<route>/<year>/`
- manifest/audit validation of new manuscripts
- rerun of Phases 2–5 on expanded corpus

No new compliance boundary was introduced by cleanup or metrics hardening. The beta pilot protocol adds explicit intake controls but does not change the underlying need for lawful access and conservative retrieval behavior.

---

# 3. Lawful Data Access

Before processing any new document source, confirm:
- the source is legally accessible
- access complies with publisher or repository policy
- no paywall protections are bypassed
- institutional subscription access is respected where applicable

---

# 4. Corpus Usage Boundaries

The corpus is used for computational analysis only.

Restrictions:
- do not redistribute publisher PDFs
- do not republish extracted full texts as corpus outputs
- do not use the corpus to train commercial AI systems
- publish analytical results, not redistributed source content

This rule applies equally to pilot-acquired files and the validated benchmark corpus.

---

# 5. Benchmark vs Beta vs Testing Separation

These domains must remain distinct.

## Existing validated benchmark corpus
- `data/raw/`
- current validated production-like benchmark artifacts under `processed/`, `structured/`, `embeddings/`, and `metrics/`

## Beta pilot live-manuscript corpus
- `data/raw_pdfs/<route>/<year>/...`

## Testing corpus
- `data/testing/doi_abstracts_2021_2026/`

Compliance rules:
- beta pilot files must not be silently merged into the benchmark corpus
- testing artifacts must not be silently promoted into production-like analysis state
- pilot intake decisions must be auditable

---

# 6. Beta Pilot Safeguards

Required beta safeguards:
- controlled smaller corpus, not broad uncontrolled scrape
- explicit pilot protocol
- route/year intake rules
- provenance capture for each file
- no hidden fallback output paths
- stop on mismatch or uncertainty
- quarantine unresolved items rather than silently admitting them

Beta pilot should not be represented as inferential historical evidence by itself.

---

# 7. Provenance Expectations

Where source metadata is available, track:
- source URL
- publisher / host
- DOI
- source identifier
- acquisition batch identifier
- resolved route
- resolved year
- destination path
- quarantine or acceptance status

For pilot intake, provenance must be logged before the manuscript is treated as part of the active pilot corpus.

---

# 8. Network Use Safeguards

If automated acquisition is implemented or expanded, include:
- request rate limiting
- retry limits
- exponential backoff
- randomized delay behavior where appropriate
- API identification headers where required
- contact information in user-agent metadata where appropriate

Conservative target request rate:
- 1–2 requests per second maximum

Illustrative settings:

```python
MAX_REQUESTS_PER_SECOND = 2
REQUEST_BACKOFF = True
RETRY_LIMIT = 3
```

---

# 9. System Integrity Expectations

Before integrating new modules or changing stage contracts, verify:
- deterministic behavior is preserved
- benchmark/regression coverage remains valid
- new code does not bypass manifest tracking
- schema and artifact boundaries remain explicit
- documentation reflects implemented code state rather than scaffold or plan state
- beta pilot intake remains isolated, deterministic, and auditable

# Research Compliance

Version: 2.2
Date: 2026-03-20
Status: Supplemental compliance reference aligned to the stabilized Phase 5 state and the active beta pilot epoch protocol

---

# 1. Purpose

Core priorities:
- lawful data access
- respect for publisher and repository terms
- conservative network behavior
- reproducible processing
- auditable artifact generation
- clear separation of benchmark corpus, beta pilot corpus, and testing corpora

---

# 2. Current Operational Scope

Current implemented workflow covers:
- local corpus processing
- extraction and cleaning
- segmentation and structured export
- section embedding generation
- route-level metrics computation

Defined and now partially executed:
- live-manuscript intake under `data/raw/<route>/<year>/`
- manifest/audit validation of new manuscripts
- rerun of Phases 2–5 on expanded corpus

No new compliance boundary was introduced by cleanup or metrics hardening. The beta pilot protocol adds explicit intake controls but does not change the underlying need for lawful access and conservative retrieval behavior.

---

# 3. Lawful Data Access

Before processing any new document source, confirm:
- the source is legally accessible
- access complies with publisher or repository policy
- no paywall protections are bypassed
- institutional subscription access is respected where applicable

---

# 4. Corpus Usage Boundaries

The corpus is used for computational analysis only.

Restrictions:
- do not redistribute publisher PDFs
- do not republish extracted full texts as corpus outputs
- do not use the corpus to train commercial AI systems
- publish analytical results, not redistributed source content

This rule applies equally to pilot-acquired files and the validated benchmark corpus.

---

# 5. Benchmark vs Beta vs Testing Separation

These domains must remain distinct.

## Existing validated benchmark corpus
- `data/raw/`
- current validated production-like benchmark artifacts under `processed/`, `structured/`, `embeddings/`, and `metrics/`

## Current live intake / promoted corpus
- `data/raw/<route>/<year>/...`

Historical note:
- earlier beta-planning documents referenced `data/raw_pdfs/<route>/<year>/...`
- the executed 1960–1969 legacy batch was intentionally promoted into `data/raw/Route_B_Legacy/` and bridged into the live pipeline manifest

## Testing corpus
- `data/testing/doi_abstracts_2021_2026/`

Compliance rules:
- beta pilot files must not be silently merged into the benchmark corpus
- testing artifacts must not be silently promoted into production-like analysis state
- pilot intake decisions must be auditable

---

# 6. Beta Pilot Safeguards

Required beta safeguards:
- controlled smaller corpus, not broad uncontrolled scrape
- explicit pilot protocol
- route/year intake rules
- provenance capture for each file
- no hidden fallback output paths
- stop on mismatch or uncertainty
- quarantine unresolved items rather than silently admitting them

Beta pilot should not be represented as inferential historical evidence by itself.

---

# 7. Provenance Expectations

Where source metadata is available, track:
- source URL
- publisher / host
- DOI
- source identifier
- acquisition batch identifier
- resolved route
- resolved year
- destination path
- quarantine or acceptance status

For pilot intake, provenance must be logged before the manuscript is treated as part of the active pilot corpus.

---

# 8. Network Use Safeguards

If automated acquisition is implemented or expanded, include:
- request rate limiting
- retry limits
- exponential backoff
- randomized delay behavior where appropriate
- API identification headers where required
- contact information in user-agent metadata where appropriate

Conservative target request rate:
- 1–2 requests per second maximum

Illustrative settings:

```python
MAX_REQUESTS_PER_SECOND = 2
REQUEST_BACKOFF = True
RETRY_LIMIT = 3
```

---

# 9. System Integrity Expectations

Before integrating new modules or changing stage contracts, verify:
- deterministic behavior is preserved
- benchmark/regression coverage remains valid
- new code does not bypass manifest tracking
- schema and artifact boundaries remain explicit
- documentation reflects implemented code state rather than scaffold or plan state
- beta pilot intake remains isolated, deterministic, and auditable


---

# 10. Legacy Batch Execution Note

The 1960–1969 legacy acquisition batch has now been executed under the live intake workflow.

Verified result:
- 149 legacy PDFs promoted into `data/raw/Route_B_Legacy/<year>/`
- 149 rows bridged into `data/manifests/pipeline_manifest.csv`

Compliance implication:
- this batch is no longer merely a protocol/planning example
- provenance and promotion decisions must continue to remain auditable at row level

---

# DATA EXCLUSION AND METRIC INTEGRITY

The pipeline enforces exclusion of documents that do not resolve to valid temporal metadata.

Example:
- `Vol1_1.pdf` (no year information)

Compliance rationale:
- inclusion would corrupt longitudinal analysis
- violates reproducibility and interpretability constraints

Operational rule:
- such documents are skipped prior to processing
- exclusion is logged
- no derived artifacts are produced for excluded files

This ensures:
- consistent temporal indexing
- valid metric aggregation
- reproducible analytical outputs

---
