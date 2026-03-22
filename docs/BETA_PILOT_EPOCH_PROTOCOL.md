# BETA PILOT EPOCH PROTOCOL

Version: 1.1
Date: 2026-03-20
Status: Active beta pilot methodology for live-manuscript engine testing

---

## 1. Purpose

This protocol defines the beta pilot study for the JAE_Legacy_Audit project.

This pilot is **not** designed to support validated inferential claims about historical semantic change. It is a **live-manuscript beta systems test** designed to verify that the engine functions correctly end-to-end on a controlled smaller corpus while larger ingestion continues.

Primary objective:
- verify engine correctness, contract integrity, and reproducible epoch behavior on live manuscripts

Non-objective:
- population-level inference
- formal hypothesis testing
- strong historical trend claims

---

## 2. Canonical Corpus Organization

Active raw-manuscript storage rule:

```text
data/raw_pdfs/<route>/<year>/<filename>.pdf
```

Examples:

```text
data/raw_pdfs/Route_A_Modern/2025/<file>.pdf
data/raw_pdfs/Route_B_Legacy/1960/<file>.pdf
```

Rules:
- manuscripts are grouped by `route` and single resolved integer `year`
- manuscripts are **not** stored by epoch folder
- epoch assignment happens later during metrics processing
- all active paths must resolve under the NVMe project root

Allowed route names:
- `Route_A_Modern`
- `Route_B_Legacy`

Project year bounds:
- `1960` through `2026`

---

## 3. Intake Control Manifest

Control template path:

```text
data/manifests/beta_sample_manifest_template.csv
```

Required control fields include:
- `beta_batch_id`
- `sample_id`
- `route_target`
- `sampling_bucket`
- `risk_class`
- `source_host`
- `source_url`
- `source_identifier`
- `expected_filename`
- `destination_stage_path`
- `planned_year`
- `manual_review_status`
- `download_status`
- `promotion_candidate`
- `promotion_status`
- `notes`

Operational rule:
- no manuscript enters the active pilot corpus without an intake-control record

---

## 4. Year Resolution Rule

Year must be resolved using this precedence:
1. explicit authoritative year / manifest year
2. legacy year map
3. supported filename parsing
4. fail and quarantine if unresolved

Operational rules:
- each manuscript must have exactly one resolved year
- unresolved-year manuscripts do not enter the active pilot corpus
- manifest year is the authoritative year used downstream
- embedding bundles do not supply the authoritative year for Phase 5

---

## 5. Epoch Rule

Epochs are deterministic 5-year closed bins anchored at 1960.

Examples:
- `1960 -> 1960-1964`
- `1964 -> 1960-1964`
- `1965 -> 1965-1969`
- `2025 -> 2025-2029`
- `2026 -> 2025-2029`

Operational rule:
- raw corpus organization is by year
- analysis grouping is by derived epoch

---

## 6. Eligibility and Quarantine Criteria

### Inclusion criteria
A manuscript is eligible for the beta pilot if it has:
- a valid PDF
- a resolvable route
- a resolvable year
- a unique `doc_id`
- a source path under the NVMe project root
- a valid manifest/control row

### Quarantine criteria
A manuscript must be excluded from the active pilot if any of the following apply:
- route unresolved
- year unresolved
- year out of bounds
- duplicate `doc_id`
- duplicate source path with unresolved conflict
- corrupted or unreadable PDF
- manifest/path mismatch

Excluded items must be logged, not silently dropped.

---

## 7. Pilot Sampling Strategy

This is a purposeful engineering sample, not a random inferential sample.

Target pilot characteristics:
- both routes represented
- multiple publication years if available
- heterogeneous PDF characteristics
- at least one route with more than one realized epoch if the live corpus allows it

Recommended default beta design:
- 16 total PDFs
- 6 modern typical cases
- 4 legacy typical cases
- 4 high-risk / edge / deviant cases
- 2 random audit cases

---

## 8. Workflow

### Stage 0 — Intake staging
1. collect live manuscript PDFs
2. resolve route and year
3. move files into canonical route/year layout
4. seed or update control/manifest rows

### Stage 1 — Intake audit
Generate a pre-pipeline summary containing:
- manuscript count by route
- manuscript count by year
- manuscript count by prospective epoch
- duplicate/conflict count
- unresolved/quarantined count

### Stage 2 — Pipeline execution
Run the pilot corpus through:
- extraction
- structured section export
- section embeddings
- Phase 5 route-level metrics generation

### Stage 3 — Post-Phase-5 validation
Validate:
- metrics artifact structure
- route consistency
- manifest consistency
- deterministic epoch grouping
- acceptance of valid singleton-epoch artifacts where applicable

### Stage 4 — Pilot summary
Produce a pilot closeout summary including:
- manuscripts processed
- manuscripts quarantined
- route/year/epoch coverage
- artifact validity outcomes
- engine failures or manual interventions
- recommendation for scale-up or further repair

---

## 9. Primary Outcomes

Primary operational outcomes:
1. ingestion success rate
2. year resolution success rate
3. manifest integrity rate
4. Phase 2–5 completion rate on the pilot corpus
5. route-level metrics artifact validation success
6. realized epoch count by route

Secondary operational outcomes:
1. duplicate/conflict rate
2. quarantine rate
3. extraction failure rate
4. embedding failure rate
5. metrics failure rate
6. manual intervention count

---

## 10. Success / Failure Criteria

### Pilot success
The pilot is successful if:
- manuscripts are staged under canonical route/year organization
- manifest/control rows are complete and valid
- Phases 2–5 execute on the pilot corpus
- route-level metrics artifacts are generated
- post-Phase-5 validation passes
- reruns are deterministic
- logs and handoff docs can be updated

### Pilot failure / hold
The pilot remains incomplete if:
- unresolved route/year conflicts persist
- corpus placement is nondeterministic
- post-Phase-5 validation fails
- outputs require undocumented manual intervention
- provenance or control records are incomplete

---

## 11. Phase 6 Gate

The pilot may justify broader Phase 6 work only if live-manuscript ingestion expands route coverage enough to produce analytically meaningful multi-epoch route behavior.

If routes remain singleton-epoch after pilot ingestion, Phase 6 should remain descriptive/readiness-oriented.
