# Computational Infrastructure Audit

**Project:** A Semantic MRI of Agricultural Education
**Author:** Christopher Clemons
**Build Date:** 2026-03-10

---

# 1. System Metadata

## Hardware

CPU: Apple M3 Max
Memory: 64GB Unified Memory

## Storage

Primary Storage: External NVMe
Volume Name: `Clemons_Data`

Physical Project Root:

```
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

Logical Anchor:

```
~/_Anchors/Research_Data/JAE_Legacy_Audit
```

---

## Python Environment

Python Version:

```
python3 --version
```

Example output:

```
Python 3.x.x
```

Compute Device:

```
DEVICE = "mps"
```

Metal Performance Shaders (Apple Silicon GPU acceleration)

Embedding Model:

```
nomic-ai/nomic-embed-text-v1.5
```

Context Window:

```
TOKEN_LIMIT = 8192
```

Worker Pool:

```
MAX_WORKERS = 8
```

Workers were intentionally throttled from 14 to 8 to prevent unified-memory pressure and SSD swap behavior on a 64GB Apple Silicon system.

---

# 2. Infrastructure Architecture

## Storage Model

The project uses an **NVMe-backed storage architecture** with a symbolic anchor path.

This design ensures:

* large datasets remain on external high-speed storage
* the project root remains stable from the OS perspective
* compute nodes can reference a consistent path

### Physical Storage Path

```
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

### Logical Anchor Path

```
~/_Anchors/Research_Data/JAE_Legacy_Audit
```

The logical path is implemented as a **symbolic link** pointing to the NVMe storage root.

Verification command:

```
readlink ~/_Anchors/Research_Data/JAE_Legacy_Audit
```

Expected output:

```
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

---

# 3. Directory Architecture

The project follows a modular **service-bin architecture** commonly used in computational research pipelines.

```
JAE_Legacy_Audit
│
├── bins
│   ├── s01_ingest
│   │   └── orchestrator.py
│   │
│   ├── s02_processor
│   │   └── orchestrator.py
│   │
│   ├── s03_analysis
│   │   └── orchestrator.py
│   │
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
│   └── startup_check.sh
│
├── config.py
├── main.py
└── audit.md
```

---

# 4. Build Log

This section records the chronological infrastructure build steps.

---

## Step 1 — NVMe Project Root Creation

Command:

```
mkdir -p /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

Verification:

```
ls -lah /Volumes/Clemons_Data
```

Result:

macOS system metadata directories detected:

* `.DS_Store`
* `.fseventsd`
* `.Spotlight-V100`
* `.Trashes`

These are expected macOS filesystem artifacts.

---

## Step 2 — Anchor Bridge Creation

Command:

```
ln -s /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit \
~/_Anchors/Research_Data/JAE_Legacy_Audit
```

Verification:

```
readlink ~/_Anchors/Research_Data/JAE_Legacy_Audit
```

Output:

```
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

---

## Step 3 — Directory Initialization

Command:

```
mkdir -p bins/s01_ingest bins/s02_processor bins/s03_analysis bins/s04_utils
```

Additional directories:

```
data/raw/Route_A_Modern
data/raw/Route_B_Legacy
data/processed
data/manifests
logs
```

Verification:

```
find /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit -maxdepth 3
```

Result confirms directory tree creation.

---

## Step 4 — Python Package Initialization

Command:

```
touch bins/__init__.py
touch bins/s01_ingest/__init__.py
touch bins/s02_processor/__init__.py
touch bins/s03_analysis/__init__.py
touch bins/s04_utils/__init__.py
```

Purpose:

Allows secure intra-package imports within the pipeline.

---

## Step 5 — Root Configuration

`config.py` created to define:

* system paths
* embedding configuration
* hardware parameters
* runtime invariants

The project root is dynamically resolved via:

```
Path(__file__).resolve().parent
```

This prevents hard-coded filesystem assumptions.

---

## Step 6 — Root Orchestrator Creation

`main.py` created as the single command-and-control entry point.

Supported phases:

```
--phase ingest
--phase process
--phase analyze
```

Example execution:

```
python3 main.py --phase ingest
```

---

## Step 7 — Infrastructure Verification Layer

Startup validation script created:

```
scripts/startup_check.sh
```

The script validates:

* NVMe mount presence
* anchor symlink integrity
* directory structure completeness

Example output:

```
SYSTEM STATUS: READY
```

Pipeline execution is aborted if any condition fails.

---

# 5. Validation Tests

All operational phases were executed successfully.

Commands:

```
python3 main.py --phase ingest
python3 main.py --phase process
python3 main.py --phase analyze
```

Observed outputs:

```
[INGEST] Placeholder orchestrator initialized.
[PROCESS] Placeholder orchestrator initialized.
[ANALYZE] Placeholder orchestrator initialized.
```

Startup verification executed successfully in all runs.

---

# 6. Known Constraints

The pipeline assumes:

* external NVMe volume `Clemons_Data` is mounted
* anchor symlink remains intact
* Python environment includes required libraries

If the NVMe drive is not mounted, the startup verification script halts execution.

---

# 7. Reproducibility Notes

The system architecture was intentionally designed to support reproducible computational analysis.

Key design principles:

* modular phase orchestration
* hardware-aware compute configuration
* deterministic filesystem architecture
* infrastructure validation prior to pipeline execution

These practices support transparent computational methods suitable for peer-reviewed publication.

---

# 8. Git Snapshot (Recommended)

To lock the audit to a specific code state:

Run:

```
git rev-parse HEAD
```

Record the commit hash here.

```
Git Snapshot:
<commit hash>
```

---

# Status

**Phase 1 Infrastructure Build: COMPLETE**

## Phase 1.01 — Workspace Health Diagnostic

Date: 2026-03-10

Changes:
- added scripts/doctor.sh
- implemented filesystem, Python, dependency, and MPS environment checks
- established preflight health verification for the workspace

## Phase 1.01.1 — Workspace Health Diagnostic

Date: 2026-03-10

Changes:
- added scripts/doctor.sh
- implemented filesystem, Python runtime, disk capacity, dependency, and MPS checks
- validated workspace readiness before pipeline execution

Verification:
- doctor.sh returned SYSTEM STATUS: READY
- Pass: 17
- Warn: 0
- Fail: 0

Git Commit:
- 1deeb88

## Phase 1.02 — Main Orchestrator Refactor for Optional Diagnostics

Date: 2026-03-10

Changes:
- refactored main.py to support optional full workspace diagnostics
- retained startup_check.sh as the mandatory filesystem safety gate
- added --doctor / --full-check flag to invoke scripts/doctor.sh when requested

Operational effect:
- normal phase runs execute only the startup safety check
- diagnostic phase runs can invoke full workspace health validation

Verification:
- python3 main.py --phase ingest
- python3 main.py --phase process --doctor
- python3 main.py --phase analyze --full-check

## Phase 2 — Corpus Ingestion

Date: 2026-03-12

Changes:
- implemented ingestion pipeline
- added manifest generation
## Change — 2026-03-10
Implemented ingestion pipeline

Phase 2 — OCR Pipeline Debugging and Extraction Architecture Update
Date: 2026-03-14
Phase: Phase 2 – Document Extraction Reliability
Status: In Progress
Objective
Phase 2 focuses on building a reliable document extraction pipeline capable of processing the full historical corpus of agricultural education literature.
The corpus contains two distinct document classes:
Digital PDFs
Scanned archival PDFs
Both must be processed into clean corpus-ready text suitable for semantic embedding and analysis.
Corpus Test Documents
Two documents were used to validate the extraction pipeline.
Modern Digital PDF
Journal of Agricultural Education (2026)
Characteristics:
Embedded text layer
Extractable via PyMuPDF
No OCR required
Historical Scan
Journal of the American Association of Teacher Educators in Agriculture (1960)
Characteristics:
Image-only pages
No embedded text layer
Requires OCR extraction
Issues Discovered During Pipeline Audit
Variable Reference Error
Original OCR loop contained a variable mismatch.
Original code:
page_content = pytesseract.image_to_string(image)
ocr_text += page_text
Issue:
page_text was never defined.
Corrected code:
page_content = pytesseract.image_to_string(image)
ocr_text += page_content
This bug would cause the OCR pipeline to fail during runtime.
OCR Dependency Assumption
The original pipeline assumed the presence of the following system dependencies:
Tesseract OCR
Poppler (for pdf2image)
If either dependency is missing, the pipeline will fail.
Future pipeline versions must implement:
dependency detection
graceful fallback logic
Inefficient Extraction Strategy
The original workflow forced OCR for all documents.
Original architecture:
PDF → OCR → Clean text
This approach is inefficient for modern PDFs that already contain embedded text.
Updated extraction strategy:
PDF Input
   │
   ├─ Attempt PyMuPDF extraction
   │
   ├─ If extracted text length > threshold
   │        └─ Use digital text
   │
   └─ Else
          └─ Run OCR pipeline
This architecture significantly reduces processing time for modern documents.
Hard-Stop Text Cleaning Update
The pipeline includes a reference-section removal step to prevent citation lists from contaminating the semantic corpus.
Original stop markers:
References
Literature Cited
Expanded stop markers:
References
Literature Cited
Acknowledgements
Funding
This ensures the embedding corpus contains only the article body.
Phase 2 Baseline OCR Engine
Corrected OCR function:
def perform_ocr(pdf_path):

    print(f"[*] Starting OCR Engine for: {pdf_path}")

    images = convert_from_path(pdf_path, dpi=300)

    ocr_text = ""

    for i, image in enumerate(images):

        print(f"Processing page {i+1}/{len(images)}")

        page_content = pytesseract.image_to_string(image)

        ocr_text += page_content

    return ocr_text
This implementation serves as the baseline for further optimization.
Planned Extraction Engine
The final Phase 2 system will implement:
smart_extract_pdf(pdf_path)
Responsibilities:
detect digital vs scanned PDFs
route to the correct extraction method
perform OCR only when necessary
apply reference-stop cleaning
output standardized corpus-ready text
Phase 2 Progress Status
Component	Status
OCR Engine Bug Fix	Completed
Reference Cleaning	Updated
Corpus Test Validation	Completed
Smart Extraction Engine	Pending
Batch Corpus Processor	Pending