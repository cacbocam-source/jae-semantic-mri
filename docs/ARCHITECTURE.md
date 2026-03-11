# System Architecture

## Semantic MRI of Agricultural Education Pipeline

Author: Christopher Clemons
Platform: Apple Silicon (M3 Max)

---

# 1. Architectural Overview

The pipeline implements a modular computational architecture designed for large-scale semantic analysis of historical research corpora.

The system is structured around three primary operational phases:

1. **Ingestion**
2. **Processing (Vectorization)**
3. **Analysis**

All pipeline operations are orchestrated through a single entrypoint:

```
main.py
```

This design ensures that no internal module is executed directly.

---

# 2. Pipeline Flow

```
User Command
     │
     ▼
main.py (Root Orchestrator)
     │
     ├── Bin 01: Ingestion
     │
     ├── Bin 02: Processing
     │
     └── Bin 03: Analysis
```

Each bin contains an independent orchestrator module responsible for its operational domain.

---

# 3. Storage Architecture

The system uses a **dual-path storage model**.

Logical project path:

```
~/_Anchors/Research_Data/JAE_Legacy_Audit
```

Physical storage location:

```
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

The logical path is implemented as a symbolic link pointing to the NVMe-backed physical storage location.

This approach ensures:

* stable filesystem references
* large dataset storage outside the system drive
* portability of the compute environment

---

# 4. Service Bin Architecture

The pipeline is divided into modular "service bins".

```
bins/
│
├── s01_ingest
├── s02_processor
├── s03_analysis
└── s04_utils
```

Each bin is implemented as a Python package.

This architecture enables:

* modular development
* controlled imports
* independent subsystem testing

---

# 5. Data Lake Architecture

All datasets are stored within the `data` directory.

```
data/
│
├── raw
│   ├── Route_A_Modern
│   └── Route_B_Legacy
│
├── processed
│
└── manifests
```

Raw data represents unmodified corpus sources.

Processed data contains cleaned or transformed intermediate representations.

Manifests store dataset indexes and ledger records.

---

# 6. Hardware Optimization

The pipeline is optimized for Apple Silicon hardware.

Compute device:

```
Metal Performance Shaders (MPS)
```

Embedding model:

```
nomic-ai/nomic-embed-text-v1.5
```

Context window:

```
8192 tokens
```

Parallel worker count:

```
MAX_WORKERS = 8
```

Worker count was reduced from 14 to prevent unified-memory pressure on a 64GB system.

---

# 7. Infrastructure Validation

Before execution, the pipeline runs a system validation script.

```
scripts/startup_check.sh
```

The script verifies:

* NVMe drive mounted
* anchor symlink integrity
* directory structure completeness

Pipeline execution is halted if validation fails.

---

# 8. Root Configuration

All system configuration values are defined in:

```
config.py
```

The project root is dynamically resolved using:

```
Path(__file__).resolve().parent
```

This removes hard-coded filesystem assumptions and improves portability.

---

# 9. Command Interface

The pipeline is executed via CLI commands.

Examples:

```
python3 main.py --phase ingest
python3 main.py --phase process
python3 main.py --phase analyze
```

Each command triggers the corresponding service bin.

---

# 10. Design Principles

The architecture follows several guiding principles:

* modular service boundaries
* deterministic filesystem layout
* hardware-aware computation
* infrastructure validation before execution
* reproducible computational environments

---

# Status

Architecture Version: 1.0
