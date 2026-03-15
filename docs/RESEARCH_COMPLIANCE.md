1. Research Compliance Note
project purpose
data sources
access permissions
API policies followed
rate limits used

2. Network Safety Settings
When you eventually build acquisition scripts, include:
MAX_REQUESTS_PER_SECOND = 2
REQUEST_BACKOFF = True
RETRY_LIMIT = 3


3. Corpus Usage Policy

Document internally:
The corpus is used only for computational analysis.
No publisher content will be redistributed.

4. In your ledger track:
doi
publisher
source_url
license_type

This strengthens provenance tracking.

## Research Transparency Development Checklist

This checklist must be reviewed before implementing any new module,
automation component, or corpus acquisition process.

The purpose is to ensure that all system development maintains the
highest academic research standards and complies with publisher,
API, and institutional network policies.

------------------------------------------------------------

### 1. Lawful Data Access

Before processing any new document source confirm:

□ The document source is legally accessible.
□ Access complies with publisher or repository policies.
□ No paywall protections are bypassed.
□ Institutional subscription access is respected.

If uncertain, consult the university library or research compliance office.

------------------------------------------------------------

### 2. Publisher and API Compliance

Before implementing any automated data acquisition:

□ The API terms of service have been reviewed.
□ Request rates are within recommended limits.
□ API identification headers are included.
□ Contact email is provided in User-Agent.

Example:

User-Agent: JAE-Legacy-Audit-Research/1.0
Contact: your.email@university.edu

------------------------------------------------------------

### 3. Network Safety

All automated acquisition must include safeguards.

Required protections:

□ Request rate limiting implemented.
□ Retry limits implemented.
□ Exponential backoff enabled.
□ Randomized delays between requests.

Target request rate:

1–2 requests per second maximum.

This prevents denial-of-service behavior and protects institutional networks.

------------------------------------------------------------

### 4. Corpus Usage Boundaries

The corpus is used exclusively for computational research.

Restrictions:

□ No redistribution of publisher PDFs.
□ No republishing of extracted full texts.
□ No use of corpus to train commercial AI systems.
□ Only analytical results will be published.

------------------------------------------------------------

### 5. Reproducibility and Auditability

All processing must be traceable.

Verify:

□ Source PDF recorded in ledger.
□ Extraction method recorded.
□ Processing timestamp recorded.
□ Generated artifacts stored in processed corpus directory.
□ System changes recorded in docs/audit.md.

------------------------------------------------------------

### 6. System Integrity

Before integrating new modules confirm:

□ Code passes benchmark diagnostics.
□ Processing pipeline remains deterministic.
□ New module does not bypass the ledger system.
□ New module integrates with existing architecture.

------------------------------------------------------------

### 7. Institutional Compliance

If uncertainty exists regarding network usage, licensing,
or data access policies, consult:

• University Library Scholarly Communications
• Institutional Research Compliance Office
• University IT Network Policy Documentation

------------------------------------------------------------

### Final Principle

This project prioritizes:

• research transparency
• ethical data handling
• reproducibility
• respect for publisher infrastructure
• compliance with institutional policies