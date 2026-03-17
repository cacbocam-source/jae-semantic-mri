# SEMANTIC MRI PIPELINE — PROJECT STATE AUDIT
Version: 1.0
Date: 2026-03-17

This document provides a deterministic snapshot of the system architecture,
methodology, engineering status, and next steps so a new AI session can restore
full operational context instantly.

The assistant must treat this document as authoritative project state.

---

# PROJECT IDENTITY

Project Name  
Semantic MRI of Agricultural Education

Full Title  
A Semantic MRI of Agricultural Education:  
A Longitudinal Audit of Evolutionary Maturation, Methodological Friction, and Innovation Velocity (1960–2026) via High-Dimensional Vector Embeddings

Research Objective  
Measure the semantic evolution of agricultural education research using
high-dimensional vector embeddings applied to journal manuscript sections.

Primary Measurements

• Semantic dispersion  
• Innovation velocity  
• Epoch centroid drift

Corpus

Journal of Agricultural Education manuscripts

Temporal Scope

1960–2026

Epoch Structure

5-year epochs

---

# COMPUTATIONAL PHILOSOPHY

The pipeline is designed for:

• deterministic computation  
• full reproducibility  
• transparent mathematics  
• auditability  
• hardware-aware acceleration

The system intentionally avoids:

• black-box ML pipelines  
• opaque vector frameworks  
• undocumented tensor math

All vector calculations must use verified scientific libraries.

Approved libraries
numpy
scipy.spatial.distance


---

# HARDWARE ENVIRONMENT

Primary Compute System

Apple Silicon M3 Max  
64 GB unified memory

Acceleration


DEVICE = "mps"


Embedding Model


nomic-ai/nomic-embed-text-v1.5


Model Properties

• 768-dimensional embeddings  
• 8k token context window  
• suitable for long scientific text

---

# PROJECT ROOT

Primary workspace


/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit


---

# REPOSITORY ARCHITECTURE


JAE_Legacy_Audit
│
├── bins
│ ├── s01_ingest
│ ├── s02_processor
│ ├── s03_analysis
│ └── s04_utils
│
├── data
│ ├── raw
│ ├── processed
│ ├── structured
│ ├── manifests
│ └── testing
│
├── docs
├── logs
├── manuscript
├── scripts
├── tests
│
├── config.py
└── main.py


---

# CURRENT PROJECT STATE

## Phase 1 — Infrastructure

Status: COMPLETE

Components

• repository architecture  
• config system  
• ledger system  
• directory idempotency guards  
• backup architecture

---

## Phase 2 — Extraction Pipeline

Status: COMPLETE

Location


bins/s02_processor


Modules


digital_extract.py
ocr_engine.py
smart_extract.py
cleaning.py
segmenter.py


Capabilities

• digital text extraction  
• OCR fallback  
• reference truncation  
• era-aware segmentation

OCR configuration


OCR_DPI = 300
TESSERACT_LANG = "eng"


Reference removal rule

Text is truncated at:

• References  
• Literature Cited  
• Acknowledgements  
• Funding

---

## Era-Aware Segmentation Logic

### 1960–1979

Heuristic segmentation


Intro = first 30%
Results = final 40%


### 1980–2004

Fuzzy header detection


Methodology
Purpose
Need for Study


### 2005–2026

Strict header matching


Introduction
Theoretical Framework
Results
Findings
Discussion


---

## Phase 2 Output


data/processed/


Example


Route_A_Modern/2026.txt
Route_B_Legacy/Vol1_1.txt


Validation


tests/test_benchmarks.py


Result


Passed 5/5 tests


---

## Phase 3 — Structured Export

Status: COMPLETE

Location


bins/s03_analysis


Modules


section_export.py
orchestrator.py


Purpose

Convert manuscripts into structured JSON objects.

Fields


doc_id
route
A_intro
A_results
page_count
extraction_method


Output


data/structured/


Example


Route_A_Modern/2026.json
Route_B_Legacy/Vol1_1.json


Validation


tests/test_section_exports.py


Result


Passed 2/2 tests


---

# MATHEMATICAL FRAMEWORK

Translation from methodology to Python is fixed.

## Epoch Centroid


epoch_centroid = np.mean(epoch_vectors, axis=0)


Axis must equal zero.

---

## Cosine Distance


distance.cosine(vector_A, vector_B)


Scipy implementation prevents floating-point drift.

---

## Semantic Dispersion

Vectorized computation required.


cdist(epoch_vectors, centroid)


Loop implementations are prohibited.

---

## Innovation Velocity


distance.cosine(centroid_T, centroid_T_plus_1)


---

# TEST CORPUS (PIPELINE VALIDATION)

A separate dataset is used for testing.

Contents

1400 records


title
abstract
keywords


Coverage


2021–2026


Purpose

• embedding pipeline testing  
• performance validation  
• metric sanity checks

Location


data/testing/doi_abstracts_2021_2026


Structure


raw
structured
embeddings
metrics


This dataset must **never be merged with the main corpus.**

---

# BACKUP ARCHITECTURE

3-2-1 research backup system implemented.

Primary workspace


Clemons_Data (NVMe)


Local redundancy


Laptop SSD


Mirror archive


Veri-Intent-Core external SSD


Version control


GitHub repository


Backup scripts


/Volumes/Veri-Intent-Core/Backup_Scripts


Scripts


nvme_mirror.sh
integrity_check.sh


Integrity logs


/Volumes/Veri-Intent-Core/Integrity_Logs


---

# GIT WORKFLOW

Manual commit strategy.

Snapshot script


scripts/research_snapshot.sh


Purpose

• stage changes  
• commit milestone  
• push to GitHub

---

# CURRENT ENGINEERING STATE

Completed


Infrastructure
Extraction
Segmentation
Structured export
Regression tests
Backup architecture


Pending


Embedding engine
Vector metrics
Statistical inference


---

# NEXT ENGINEERING TASKS

## Phase 4 — Embedding Engine

File


bins/s03_analysis/embedder.py


Input


data/structured/*.json


Output


data/embeddings/


---

## Phase 5 — Vector Metrics

File


bins/s03_analysis/metrics.py


Calculations

• epoch centroids  
• semantic dispersion  
• innovation velocity

---

## Phase 6 — Statistical Inference

File


bins/s03_analysis/statistics.py


Tests


Kruskal-Wallis
Pettitt change-point


---

# CURRENT DAY DEVELOPMENT TARGET

Immediate task


Phase 4.1 — build embedder.py


After embedder works

Run stress test using


1400 DOI abstract dataset


This validates

• embedding throughput  
• vector dimensional stability  
• metrics pipeline

---

# INSTRUCTIONS FOR FUTURE AI SESSIONS

The assistant must:

1. Treat this document as authoritative project state.
2. Maintain compatibility with existing architecture.
3. Preserve deterministic vector mathematics.
4. Keep testing corpus separate from the main corpus.
5. Avoid introducing black-box ML frameworks.

All development must respect these constraints.

Audit Context Update — Phase 4.1 Bring-Up (Embedding Pipeline)
Summary

During Phase 4 development of the Semantic MRI pipeline, several structural mismatches between the audit specification and the implemented codebase were discovered and corrected. These changes are now considered the canonical operational design.

1. Section Schema Normalization

The segmentation system outputs the following canonical fields:

A_intro
A_methods
A_results

These correspond to the conceptual audit sections:

Introduction
Methods
Results / Discussion

The lowercase schema is now standard across the pipeline.

Rationale

This avoids mixed casing inconsistencies observed during early integration:

A_Intro vs A_intro
A_Results vs A_results

All modules must reference:

A_intro
A_methods
A_results
2. Structured Export Schema Correction

section_export.py previously serialized sections as:

{
  "sections": {
    "A_intro": "...",
    "A_results": "..."
  }
}

This prevented the embedding stage from locating section text.

Correct Export Schema

Sections are now flattened into the root JSON:

{
  "doc_id": "...",
  "route": "...",
  "A_intro": "...",
  "A_methods": "...",
  "A_results": "..."
}

This matches the assumptions used by embedder.py.

3. Verified Pipeline Flow

The validated pipeline sequence is now:

PDF (data/raw)

→ smart_extract_pdf()
   bins/s02_processor/smart_extract.py

→ UniversalSegmenter
   bins/s02_processor/segmenter.py

→ section_export
   bins/s03_analysis/section_export.py

→ embedder
   bins/s03_analysis/embedder.py

→ embeddings/*.npz
4. Embedding Bundle Format

Each document produces a compressed .npz bundle containing:

doc_id
route
section_labels
embeddings

Example structure:

data/embeddings/
 ├── Route_A_Modern/
 │   └── jae_90944b221a70.npz
 └── Route_B_Legacy/
     └── jae_e53ec5d6271f.npz

Each .npz stores:

embeddings: ndarray (n_sections × embedding_dim)
section_labels: list[str]
5. Phase 4.1 Status

Embedding generation is now confirmed operational.

Validation run:

structured JSONs processed: 2
embeddings generated: 2
errors: 0

Pipeline components verified:

extraction

segmentation

structured export

embedding generation

6. Next Development Step

The next component to implement is:

bins/s03_analysis/metrics.py

This module will compute:

epoch centroids
semantic dispersion
innovation velocity

using the embeddings produced by Phase 4.1.

### 2026-03-17 — Structured Schema Hardening (Segmentation → Embedding Pipeline)

**Issue**

The embedding stage skipped all records even though segmentation succeeded.
Root cause: **schema drift between pipeline stages**.

`segmenter.py` produced section outputs inside a nested structure:

```
segmentation.sections["A_intro"]
segmentation.sections["A_results"]
```

However `embedder.py` expected **top-level JSON keys**:

```
payload["A_intro"]
payload["A_results"]
```

Because `section_export.py` wrote the nested structure directly, the embedder saw empty values and skipped all documents.

**Observed symptom**

```
[SKIP] <doc_id> contains no embeddable section text
Embedding complete. Wrote 0 files
```

**Resolution**

A canonical schema layer was introduced in:

```
bins/s04_utils/
```

Key components:

```
schemas.py
validators.py
```

These define:

```
A_INTRO
A_METHODS
A_RESULTS
ROUTE_MODERN
ROUTE_LEGACY
VALID_ROUTES
SECTION_NOT_FOUND
```

All downstream modules now import schema constants rather than using literal strings.

**Pipeline changes**

`segmenter.py`

* Produces canonical section mapping

`section_export.py`

* Flattens sections into top-level JSON fields
* Validates payload with `validate_structured_payload()`

`embedder.py`

* Uses schema constants instead of string literals
* Uses `is_real_section_text()` to filter placeholder values

**Architectural rule**

Pipeline modules must **never hardcode schema keys**.

Instead import from:

```
bins.s04_utils.schemas
```

This prevents silent pipeline breakage when schema evolves.

**Bug class eliminated**

Schema drift across pipeline stages.

Without centralized constants, changes in segmentation output structure can silently invalidate downstream processing.

**Status**

Pipeline validated end-to-end:

```
structured → embeddings
```

Example output:

```
data/embeddings/
 ├─ Route_A_Modern/jae_90944b221a70.npz
 └─ Route_B_Legacy/jae_e53ec5d6271f.npz
```

Embedding generation now succeeds with no skips.

## Canonical Structured Section Schema

Structured JSON artifacts produced by `bins/s03_analysis/section_export.py`
follow the canonical flattened schema:

{
  "doc_id": "...",
  "source_filename": "...",
  "source_pdf_path": "...",
  "route": "Route_A_Modern | Route_B_Legacy",
  "year": 2026,
  "extraction_method": "fitz | ocr",
  "page_count": 18,
  "raw_text_length": 45012,
  "clean_text_length": 39210,
  "segmentation_strategy": "...",

  "A_intro": "...",
  "A_methods": "...",
  "A_results": "..."
}
Canonical section keys:

A_intro  
A_methods  
A_results

These replace earlier nested structures such as:

"sections": {
  "A_Intro": "...",
  "A_Methods": "...",
  "A_Results": "..."
}
The legacy nested schema is no longer produced by the pipeline.