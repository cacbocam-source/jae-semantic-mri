# Pipeline Audit and Validation Record

- generated_at_utc: `2026-05-22T14:01:29.671319+00:00`
- project: `JAE_Legacy_Audit`
- system: `Semantic MRI Pipeline`

## Pipeline Workflow

1. Stage one target year in a clean folder
2. Run `scripts/run_route_a_year.py`
3. Inspect the Route_A dashboard artifacts

## Automated Year Loop Coverage

- integrated_year_count: `9`
- missing_year_count: `18`
- integrated_years: `2000, 2001, 2003, 2007, 2012, 2013, 2022, 2024, 2026`

## Current Invariants

- Raw PDFs are normalized with `YYYY_` prefix for article-level years
- Manifest admission uses canonical `doc_id` generation
- Year-gap is derived from the rebuilt Route_A ledger
- Metrics and Phase 6 outputs are regenerated after each completed year loop
- APA artifacts are rebuilt after each metrics refresh

## Known Required Environment

- Repo root must be the working directory
- `PYTHONPATH=.` is required for direct module execution outside `main.py`

## Current Missing Years

2002, 2004, 2005, 2006, 2008, 2009, 2010, 2011, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2023, 2025

