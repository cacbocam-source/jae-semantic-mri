Computational Infrastructure Audit

Project: A Semantic MRI of Agricultural Education
Author: Christopher Clemons
Initial Build Date: 2026-03-10

1. System Metadata
Hardware

CPU: Apple M3 Max
Memory: 64GB Unified Memory

Storage

Primary Storage: External NVMe
Volume Name:

Clemons_Data

Physical Project Root

/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit

Logical Anchor

~/_Anchors/Research_Data/JAE_Legacy_Audit
Python Environment

Python Version

python3 --version

Compute Device

DEVICE = "mps"

Apple Metal Performance Shaders GPU acceleration.

Embedding Model

nomic-ai/nomic-embed-text-v1.5

Context Window

TOKEN_LIMIT = 8192

Worker Pool

MAX_WORKERS = 8

Workers were intentionally reduced from 14 to 8 to prevent unified-memory pressure on a 64GB Apple Silicon architecture.

2. Infrastructure Architecture
Storage Model

The system uses an NVMe-backed storage architecture combined with a symbolic anchor path.

Benefits:

• large corpus storage on high-speed external NVMe
• stable OS-level project path
• reproducible compute paths

Physical Storage
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
Logical Anchor
~/_Anchors/Research_Data/JAE_Legacy_Audit

Verification command

readlink ~/_Anchors/Research_Data/JAE_Legacy_Audit

Expected output

/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
3. Directory Architecture

The system follows a modular service-bin pipeline architecture.

JAE_Legacy_Audit
│
├── bins
│   ├── s01_ingest
│   ├── s02_processor
│   ├── s03_analysis
│   └── s04_utils
│
├── data
│   ├── raw
│   │   ├── Route_A_Modern
│   │   └── Route_B_Legacy
│   │
│   ├── processed
│   └── manifests
│
├── logs
├── scripts
│
├── config.py
├── main.py
└── docs/audit.md
4. Phase 1 — Infrastructure Build
Step 1 — NVMe Project Root
mkdir -p /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
Step 2 — Anchor Bridge
ln -s /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit \
~/_Anchors/Research_Data/JAE_Legacy_Audit

Verification

readlink ~/_Anchors/Research_Data/JAE_Legacy_Audit
Step 3 — Directory Initialization
mkdir -p bins/s01_ingest bins/s02_processor bins/s03_analysis bins/s04_utils

Additional directories

data/raw/Route_A_Modern
data/raw/Route_B_Legacy
data/processed
data/manifests
logs
Step 4 — Python Package Initialization
touch bins/__init__.py
touch bins/s01_ingest/__init__.py
touch bins/s02_processor/__init__.py
touch bins/s03_analysis/__init__.py
touch bins/s04_utils/__init__.py
Step 5 — Root Configuration

config.py created to centralize:

• system paths
• compute configuration
• embedding parameters
• runtime invariants

Project root resolved dynamically:

Path(__file__).resolve().parent
Step 6 — Root Orchestrator

main.py created as the global execution entry point.

Supported phases

--phase ingest
--phase process
--phase analyze

Example

python3 main.py --phase ingest
Step 7 — Infrastructure Safety Layer

Startup validation script

scripts/startup_check.sh

Checks:

• NVMe mount
• symlink integrity
• directory structure
• compliance safeguards

Phase 1 Status

Phase 1 Infrastructure Build: COMPLETE

Phase 1.01 — Workspace Health Diagnostic

Date: 2026-03-10

Implemented:

scripts/doctor.sh

Checks include:

• filesystem integrity
• Python runtime
• disk capacity
• dependencies
• MPS availability

Result

SYSTEM STATUS: READY
Phase 1.02 — Orchestrator Diagnostic Refactor

Date: 2026-03-10

main.py updated to support optional diagnostics.

Flags

--doctor
--full-check

This enables controlled execution of full system health checks when needed.

Phase 2 — Smart PDF Extraction Engine

Date: 2026-03-14

Objective

Create a robust extraction engine capable of processing both:

• digital PDFs
• scanned archival PDFs

Extraction Strategy

Pipeline logic

PDF
 │
 ├─ attempt PyMuPDF extraction
 │
 ├─ if sufficient text found
 │      use digital extraction
 │
 └─ else
        fallback to OCR
Implemented Processor Modules
bins/s02_processor/cleaning.py
bins/s02_processor/digital_extract.py
bins/s02_processor/ocr_engine.py
bins/s02_processor/smart_extract.py
bins/s02_processor/diagnostics.py
bins/s02_processor/orchestrator.py

External dependencies validated

• PyMuPDF
• Tesseract
• Poppler
• pytesseract
• pdf2image

Cleaning Pipeline

Hard-stop truncation removes reference sections.

Stop markers

References
Literature Cited
Acknowledgements
Funding
Benchmark Validation
Modern Digital PDF

File

2026.pdf

Results

method: fitz
pages: 18
raw text: 55,599
clean text: 43,498
Legacy Scan

File

Vol1_1.pdf

Results

method: ocr
pages: 9
raw text: 31,782
clean text: 1,943
Processor Output

Generated artifacts

data/processed/Route_A_Modern/2026.txt
data/processed/Route_B_Legacy/Vol1_1.txt
Phase 2.1 — Corpus Ledger System

Date: 2026-03-14
Status: COMPLETE

Purpose

Create a deterministic corpus registry tracking all processed manuscripts.

Location

data/manifests/jae_master_ledger.csv
Implemented Modules
bins/s01_ingest/ledger.py
bins/s01_ingest/orchestrator.py
Ledger Schema
doc_id
source_filename
source_pdf_path
route
processed_text_path
extraction_method
page_count
raw_text_length
clean_text_length
status
processed_timestamp
Validation

Benchmark manuscripts registered

2026.pdf
Vol1_1.pdf

Routes verified

Route_A_Modern
Route_B_Legacy

Ledger validated using

column -s, -t < data/manifests/jae_master_ledger.csv

Phase 2.2 — Universal Segmenter

Date: 2026-03-14
Status: COMPLETE

Purpose

Convert cleaned article text into structured semantic sections used for corpus analysis.

Location

bins/s02_processor/segmenter.py
Canonical Segmentation Schema
A_TAK
A_Intro
A_Methods
A_Results
Segmentation Strategy
Legacy Manuscripts (<1985)

Technique

proximity segmentation
character fallback segmentation

Designed for OCR-derived text lacking structured headings.

Modern Manuscripts (≥1985)

Technique

regex heading detection

Detected headings include

Abstract
Introduction
Methods
Results
Discussion
Benchmark Results

Modern document

2026.pdf
A_TAK      381 chars
A_Intro    11896 chars
A_Methods  1867 chars
A_Results  42598 chars

Legacy document

Vol1_1.pdf

Segmented using OCR fallback logic.

Phase 2.3 — Benchmark Regression Tests

Status: Planned

Location

tests/test_benchmarks.py

Purpose

Ensure extraction and segmentation remain stable as the system evolves.

Tests will verify

• digital extraction route
• OCR fallback
• cleaning behavior
• segmentation correctness

Research Compliance Safeguards

Ethics and network safeguards integrated into the build workflow.

Implemented controls

docs/RESEARCH_COMPLIANCE.md
scripts/compliance_check.sh
scripts/startup_check.sh

These ensure:

• adherence to publisher policies
• conservative API usage
• transparent research practices
• institutional network compliance

Deferred Components

The following components are intentionally postponed:

bins/s01_ingest/api_harvester.py
embedding pipeline
vector index
remote corpus acquisition

These will only be implemented after:

• ledger stabilization
• segmentation validation
• regression testing

Current System Status
Component	Status
Infrastructure	COMPLETE
Extraction Engine	COMPLETE
Corpus Ledger	COMPLETE
Universal Segmenter	COMPLETE


## Change — 2026-03-15
Implemented manuscript workspace.

Created:
- manuscript/paper
- manuscript/notes
- manuscript/methods
- manuscript/references

Purpose:
Separate academic writing from engineering documentation while keeping the project on the NVMe.

## Change — 2026-03-15
Final Q and A for script verification before Phase 2.3

## Change — 2026-03-15
Final Q and A Before Closeout

## Phase 2.3 — Benchmark Regression Tests

Date: 2026-03-15  
Status: COMPLETE

Location:
`tests/test_benchmarks.py`

Purpose:
Establish automated regression tests for the benchmark corpus to ensure extraction, segmentation, and ledger registration remain stable as the pipeline evolves.

Validated benchmarks:
- `2026.pdf` (modern digital route)
- `Vol1_1.pdf` (legacy OCR route)

Tests implemented:
- modern extraction route
- legacy extraction route
- modern segmentation
- legacy segmentation
- ledger registration

Result:
All benchmark regression tests passed successfully (5/5).

## Phase 3.1 — Structured Section Export Engine

Date: 2026-03-15  
Status: COMPLETE

Location:
- `bins/s03_analysis/section_export.py`
- `bins/s03_analysis/orchestrator.py`

Purpose:
Create persistent JSON exports containing document metadata and canonical segmented text sections for downstream analytical modeling.

Structured output path:
- `data/structured/Route_A_Modern/2026.json`
- `data/structured/Route_B_Legacy/Vol1_1.json`

Validation:
- modern benchmark export passed
- legacy benchmark export passed

Result:
The analysis preparation layer now produces stable structured JSON artifacts suitable for embedding and downstream semantic analysis.

## Phase 3.1 — Structured Section Export Engine

Date: 2026-03-15  
Status: COMPLETE

Location:
- `bins/s03_analysis/section_export.py`
- `bins/s03_analysis/orchestrator.py`

Purpose:
Create persistent JSON exports containing document metadata and canonical segmented text sections for downstream analytical modeling.

Structured output path:
- `data/structured/Route_A_Modern/2026.json`
- `data/structured/Route_B_Legacy/Vol1_1.json`

Fields exported:
- document identity
- route
- inferred year
- extraction method
- page count
- raw/clean text lengths
- segmentation strategy
- canonical sections:
  - `A_TAK`
  - `A_Intro`
  - `A_Methods`
  - `A_Results`

Validation:
- modern benchmark export passed
- legacy benchmark export passed
- `tests/test_section_exports.py` passed successfully (2/2)

Result:
The analysis preparation layer now produces stable structured JSON artifacts suitable for embedding and downstream semantic analysis.