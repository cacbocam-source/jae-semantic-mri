# Legacy Acquisition Full Build — Walkthrough

## Purpose
This build converts the old abstract-only OpenAlex harvester into a full JAE_Legacy_Audit-aligned legacy acquisition layer.

It does **not** replace the stabilized core engine. It feeds that engine by producing a structured prefill queue, staged PDF downloads, canonical raw-PDF placement, and manifest-ready rows.

## Architecture
The acquisition layer now has four explicit steps:

1. `jae_openalex_prefill_builder_v2.py`
   - harvest metadata by journal and year range
   - write a structured CSV/JSONL prefill queue
   - assign `route` from year using `LEGACY_CUTOFF=2000`

2. `jae_prefill_downloader.py`
   - consume only confirmed or explicitly allowed rows
   - resolve article landing pages / PDF URLs
   - download PDFs into the staging area
   - update download status, checksum, and staged path

3. `jae_prefill_promoter.py`
   - promote approved staged files into canonical corpus storage
   - write canonical raw-PDF paths

4. `jae_prefill_manifest_bridge.py`
   - bridge promoted rows into `data/manifests/pipeline_manifest.csv`
   - prepare the new legacy corpus rows for Phases 2–5

## Canonical Paths
Project root:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

Prefill queue output root:

```text
data/staging/metadata_prefill/
```

Download staging root:

```text
data/staging/legacy_prefill_downloads/
```

Canonical raw manuscript root:

```text
data/raw_pdfs/
```

## Required File Placement
Place these four Python files into a dedicated acquisition layer such as:

```text
scripts/legacy_acquisition/
├── jae_legacy_acquisition_contract.py
├── jae_openalex_prefill_builder_v2.py
├── jae_prefill_downloader.py
├── jae_prefill_promoter.py
└── jae_prefill_manifest_bridge.py
```

The scripts are intentionally standalone so they do not modify the load-bearing `bins/s04_utils/` contract layer.

## Step 0 — Preflight
From Terminal:

```bash
cd /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
bash scripts/startup_check.sh
bash scripts/doctor.sh
```

Expected:
- `SYSTEM STATUS: READY`
- NVMe root resolved correctly

## Step 1 — Create the acquisition script directory
If needed:

```bash
mkdir -p scripts/legacy_acquisition
```

Copy the provided files into that directory.

## Step 2 — Syntax check the acquisition layer
Run:

```bash
python3 -m py_compile   scripts/legacy_acquisition/jae_legacy_acquisition_contract.py   scripts/legacy_acquisition/jae_openalex_prefill_builder_v2.py   scripts/legacy_acquisition/jae_prefill_downloader.py   scripts/legacy_acquisition/jae_prefill_promoter.py   scripts/legacy_acquisition/jae_prefill_manifest_bridge.py
```

Do not proceed until this is clean.

## Step 3 — Build the legacy prefill queue
Example: generate JAE-only legacy rows for 1960–1999.

```bash
python3 scripts/legacy_acquisition/jae_openalex_prefill_builder_v2.py   --start-year 1960   --end-year 1999   --journal-codes JAE   --write-abstract-snapshots
```

Expected outputs:

```text
data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv
data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.jsonl
data/staging/metadata_prefill/abstract_snapshots/
```

## Step 4 — Review the prefill queue before download
Open the CSV and inspect at least these columns:

- `article_title`
- `publication_year`
- `route`
- `doi`
- `article_landing_url`
- `pdf_url`
- `source_identifier`
- `manual_review_status`
- `expected_filename`
- `destination_stage_path`

Rules:
- `year < 2000` must map to `Route_B_Legacy`
- `year >= 2000` must map to `Route_A_Modern`
- unresolved rows should remain `manual_review_status=pending`
- rows with usable URLs and good metadata can remain `confirmed`

## Step 5 — Confirm or correct ambiguous rows
Before download, manually fill or correct rows where:
- `article_title` is blank or wrong
- `publication_year` is unclear
- `article_landing_url` is missing but a known article page exists
- `source_identifier` can be extracted manually from an OJS article page
- `manual_review_status` should be changed from `pending` to `confirmed`

This matches the beta workflow already proven by `beta_runner.py`: the downloader should only touch resolved rows.

## Step 6 — Download the confirmed rows into staging
Run:

```bash
python3 scripts/legacy_acquisition/jae_prefill_downloader.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv
```

What this does:
- reads the prefill queue
- skips unresolved rows by default
- downloads PDFs into the route/year staging tree
- updates:
  - `download_status`
  - `staged_pdf_path`
  - `download_date`
  - `download_http_status`
  - `downloaded_bytes`
  - `checksum_sha256`

### Dry-run mode
Use this first if you want a safe walkthrough:

```bash
python3 scripts/legacy_acquisition/jae_prefill_downloader.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv   --dry-run
```

## Step 7 — QC the staged downloads
Before promotion, review:
- file opens successfully
- correct article
- correct year folder
- no duplicate collision
- `download_status=downloaded`

At this stage, approve rows for promotion by setting:

```text
promotion_status=approved
```

Rows that fail QC should remain unpromoted.

## Step 8 — Promote approved downloads into canonical raw corpus
Run:

```bash
python3 scripts/legacy_acquisition/jae_prefill_promoter.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv
```

This copies approved staged files into:

```text
data/raw_pdfs/<route>/<year>/<filename>.pdf
```

After promotion:
- `promotion_status` becomes `promoted`
- `canonical_pdf_path` is populated

If you want to move instead of copy:

```bash
python3 scripts/legacy_acquisition/jae_prefill_promoter.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv   --move
```

## Step 9 — Bridge promoted rows into the pipeline manifest
Run:

```bash
python3 scripts/legacy_acquisition/jae_prefill_manifest_bridge.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv
```

This writes or updates rows in:

```text
data/manifests/pipeline_manifest.csv
```

Each bridged row gets:
- deterministic `doc_id`
- `source_pdf_path`
- `source_filename`
- `route`
- `year`
- phase statuses initialized to `pending`

## Step 10 — Run the stabilized core pipeline on the new batch
After manifest integration, run your existing workflow on the new legacy batch:

1. extraction
2. structured export
3. section embeddings
4. Phase 5 route-level metrics regeneration
5. post-Phase-5 validation

Do **not** modify the core engine unless an actual blocker appears.

## Step 11 — Validate the regenerated metrics artifacts
After the new batch is processed, rerun the validated metrics checks you already use.

Expected goal:
- expanded epoch coverage inside `Route_B_Legacy`
- route-level metrics artifacts still validate cleanly

## Step 12 — Update the canonical docs
After each successful acquisition batch:
- add a dated entry to `RESEARCH_LOG.md`
- update `AUDIT_CONTEXT.md`
- record:
  - batch year range
  - rows prefetched
  - rows confirmed
  - rows downloaded
  - rows promoted
  - rows bridged to manifest
  - whether epoch coverage changed

## Operational Rules
- Do not store accepted manuscripts outside the NVMe project root.
- Do not place active files into epoch folders.
- Do not bypass the prefill queue with undocumented manual placement.
- Do not run the downloader on unresolved rows without explicit review.
- Do not edit the core `bins/s04_utils/` utility layer for acquisition-only changes.

## Interpretation
This acquisition layer does not change the meaning of the core study. It formalizes the upstream corpus-capture front end so that legacy discovery/prefill is controlled, auditable, and batch-processable.

The active study still depends on full manuscript PDFs. Abstract metadata is used only to identify and resolve those manuscripts more efficiently.

# Legacy Acquisition Full Build — Walkthrough

## Purpose
This build converts the old abstract-only OpenAlex harvester into a full JAE_Legacy_Audit-aligned legacy acquisition layer.

It does **not** replace the stabilized core engine. It feeds that engine by producing a structured prefill queue, staged PDF downloads, canonical raw-PDF placement, and manifest-ready rows.

## Architecture
The acquisition layer now has four explicit steps:

1. `jae_openalex_prefill_builder_v2.py`
   - harvest metadata by journal and year range
   - write a structured CSV/JSONL prefill queue
   - assign `route` from year using `LEGACY_CUTOFF=2000`

2. `jae_prefill_downloader.py`
   - consume only confirmed or explicitly allowed rows
   - resolve article landing pages / PDF URLs
   - download PDFs into the staging area
   - update download status, checksum, and staged path

3. `jae_prefill_promoter.py`
   - promote approved staged files into canonical corpus storage
   - write canonical raw-PDF paths

4. `jae_prefill_manifest_bridge.py`
   - bridge promoted rows into `data/manifests/pipeline_manifest.csv`
   - prepare the new legacy corpus rows for Phases 2–5

## Canonical Paths
Project root:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

Prefill queue output root:

```text
data/staging/metadata_prefill/
```

Download staging root:

```text
data/staging/legacy_prefill_downloads/
```

Canonical raw manuscript root for the current live workflow:

```text
data/raw/
```

Historical note:
- earlier protocol drafts referenced `data/raw_pdfs/`
- the executed 1960–1969 batch was promoted into `data/raw/`

## Required File Placement
Place these Python files into the active acquisition layer:

```text
legacy_acquisition/
├── jae_legacy_acquisition_contract.py
├── jae_openalex_prefill_builder_v2.py
├── jae_prefill_downloader.py
├── jae_prefill_promoter.py
└── jae_prefill_manifest_bridge.py
```

The scripts are intentionally standalone so they do not modify the load-bearing `bins/s04_utils/` contract layer.

## Step 0 — Preflight
From Terminal:

```bash
cd /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
bash scripts/startup_check.sh
bash scripts/doctor.sh
```

Expected:
- `SYSTEM STATUS: READY`
- NVMe root resolved correctly

## Step 1 — Create the acquisition script directory
If needed:

```bash
mkdir -p legacy_acquisition
```

Copy the provided files into that directory.

## Step 2 — Syntax check the acquisition layer
Run:

```bash
python3 -m py_compile   legacy_acquisition/jae_legacy_acquisition_contract.py   legacy_acquisition/jae_openalex_prefill_builder_v2.py   legacy_acquisition/jae_prefill_downloader.py   legacy_acquisition/jae_prefill_promoter.py   legacy_acquisition/jae_prefill_manifest_bridge.py
```

Do not proceed until this is clean.

## Step 3 — Build the legacy prefill queue
Example: generate JAE-only legacy rows for 1960–1999.

```bash
python3 legacy_acquisition/jae_openalex_prefill_builder_v2.py   --start-year 1960   --end-year 1999   --journal-codes JAE   --write-abstract-snapshots
```

Expected outputs:

```text
data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv
data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.jsonl
data/staging/metadata_prefill/abstract_snapshots/
```

## Step 4 — Review the prefill queue before download
Open the CSV and inspect at least these columns:

- `article_title`
- `publication_year`
- `route`
- `doi`
- `article_landing_url`
- `pdf_url`
- `source_identifier`
- `manual_review_status`
- `expected_filename`
- `destination_stage_path`

Rules:
- `year < 2000` must map to `Route_B_Legacy`
- `year >= 2000` must map to `Route_A_Modern`
- unresolved rows should remain `manual_review_status=pending`
- rows with usable URLs and good metadata can remain `confirmed`

## Step 5 — Confirm or correct ambiguous rows
Before download, manually fill or correct rows where:
- `article_title` is blank or wrong
- `publication_year` is unclear
- `article_landing_url` is missing but a known article page exists
- `source_identifier` can be extracted manually from an OJS article page
- `manual_review_status` should be changed from `pending` to `confirmed`

This matches the beta workflow already proven by `beta_runner.py`: the downloader should only touch resolved rows.

## Step 6 — Download the confirmed rows into staging
Run:

```bash
python3 legacy_acquisition/jae_prefill_downloader.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv
```

What this does:
- reads the prefill queue
- skips unresolved rows by default
- downloads PDFs into the route/year staging tree
- updates:
  - `download_status`
  - `staged_pdf_path`
  - `download_date`
  - `download_http_status`
  - `downloaded_bytes`
  - `checksum_sha256`

### Dry-run mode
Use this first if you want a safe walkthrough:

```bash
python3 legacy_acquisition/jae_prefill_downloader.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv   --dry-run
```

## Step 7 — QC the staged downloads
Before promotion, review:
- file opens successfully
- correct article
- correct year folder
- no duplicate collision
- `download_status=downloaded`

At this stage, approve rows for promotion by setting:

```text
promotion_status=approved
```

Rows that fail QC should remain unpromoted.

## Step 8 — Promote approved downloads into canonical raw corpus
Run:

```bash
python3 legacy_acquisition/jae_prefill_promoter.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv
```

This copies approved staged files into:

```text
data/raw/<route>/<year>/<filename>.pdf
```

After promotion:
- `promotion_status` becomes `promoted`
- `canonical_pdf_path` is populated

If you want to move instead of copy:

```bash
python3 legacy_acquisition/jae_prefill_promoter.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv   --move
```

## Step 9 — Bridge promoted rows into the pipeline manifest
Run:

```bash
python3 legacy_acquisition/jae_prefill_manifest_bridge.py   --csv-path /Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit/data/staging/metadata_prefill/legacy_metadata_prefill_1960_1999.csv
```

This writes or updates rows in:

```text
data/manifests/pipeline_manifest.csv
```

Each bridged row gets:
- deterministic `doc_id`
- `source_pdf_path`
- `source_filename`
- `route`
- `year`
- phase statuses initialized to `pending`

## Step 10 — Run the stabilized core pipeline on the new batch
After manifest integration, run your existing workflow on the new legacy batch:

1. extraction
2. structured export
3. section embeddings
4. Phase 5 route-level metrics regeneration
5. post-Phase-5 validation

Do **not** modify the core engine unless an actual blocker appears.

## Step 11 — Validate the regenerated metrics artifacts
After the new batch is processed, rerun the validated metrics checks you already use.

Expected goal:
- expanded epoch coverage inside `Route_B_Legacy`
- route-level metrics artifacts still validate cleanly

## Step 12 — Update the canonical docs
After each successful acquisition batch:
- add a dated entry to `RESEARCH_LOG.md`
- update `AUDIT_CONTEXT.md`
- record:
  - batch year range
  - rows prefetched
  - rows confirmed
  - rows downloaded
  - rows promoted
  - rows bridged to manifest
  - whether epoch coverage changed

## Operational Rules
- Do not store accepted manuscripts outside the NVMe project root.
- Do not place active files into epoch folders.
- Do not bypass the prefill queue with undocumented manual placement.
- Do not run the downloader on unresolved rows without explicit review.
- Do not edit the core `bins/s04_utils/` utility layer for acquisition-only changes.

## Interpretation
This acquisition layer does not change the meaning of the core study. It formalizes the upstream corpus-capture front end so that legacy discovery/prefill is controlled, auditable, and batch-processable.

The active study still depends on full manuscript PDFs. Abstract metadata is used only to identify and resolve those manuscripts more efficiently.


---

## Executed milestone update

The 1960–1969 legacy batch has now been successfully executed through this workflow.

Verified outcome:
- 149 legacy PDFs downloaded into staging
- 149 legacy PDFs promoted into `data/raw/Route_B_Legacy/<year>/`
- 149 manifest rows added via the manifest bridge

This walkthrough should now be interpreted as a validated operator procedure rather than only a planned build path.