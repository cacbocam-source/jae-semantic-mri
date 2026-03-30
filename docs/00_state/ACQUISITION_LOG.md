# Acquisition Log — Route_A_Modern

> Role: Operational acquisition runbook  
> Authority: Subordinate to `AUDIT_CONTEXT.md`.  
> If this file conflicts with `AUDIT_CONTEXT.md`, the audit context controls.

## Current validated status

### Fully completed modern epoch
- `2005–2009` is the first fully reconstructed and validated modern epoch.

### Currently admitted modern year coverage
Covered:
- `2000`
- `2001`
- `2003`
- `2005`
- `2006`
- `2007`
- `2008`
- `2009`
- `2012`
- `2013`
- `2018`
- `2022`
- `2024`
- `2026`

Missing:
- `2002`
- `2004`
- `2010`
- `2011`
- `2014`
- `2015`
- `2016`
- `2017`
- `2019`
- `2020`
- `2021`
- `2023`
- `2025`

## Validated raw-storage forms

The live Route_A_Modern intake contract accepts both of these forms:

1. Flat-file modern layout  
   `data/raw/Route_A_Modern/<YEAR>.pdf`

2. Year-bucket modern layout  
   `data/raw/Route_A_Modern/<YEAR>/<file>.pdf`

## Year-resolution contract

Resolution precedence:

1. manifest year when available
2. supported filename parsing
3. supported parent-directory parsing for year-bucket modern paths
4. fail-fast unresolved state

Operational rule:

A DOI-style filename without an embedded four-digit year is valid if the file is stored under a year-bucket directory whose parent name is itself a valid year.

Example:
`data/raw/Route_A_Modern/2024/10.5032_jae.v65i4.2828.pdf -> 2024`

## Intake rules

- Accept only `.pdf` files.
- Do not treat HTML or landing pages as corpus files.
- One file = one article.
- Do not silently guess a year.
- Keep each acquisition year in its own staging folder during manual intake.
- Mixed final raw-storage forms are allowed only within the validated contract above.

## Operational workflow

1. retrieve PDFs for the target year
2. stage them in a clean per-year working folder
3. perform QC on file type and article identity
4. place accepted files into the validated Route_A_Modern raw layout
5. run manifest integration according to the active repo workflow
6. run:
   - `python3 main.py --phase process`
   - `python3 main.py --phase analyze`
7. regenerate downstream state surfaces as required by the current pipeline
8. verify outputs before treating the intake as live

## Scope note

This file is an operational runbook for acquisition-state work only.  
It does not override:
- current-state authority in `AUDIT_CONTEXT.md`
- chronology in `RESEARCH_LOG.md`
- methods/schema contracts in `METHODS_PIPELINE.md`, `DATA_SCHEMA.md`, and `SCHEMA_CONTRACT.json`
