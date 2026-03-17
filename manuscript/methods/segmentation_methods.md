### Canonical Section Representation

Extracted article sections are normalized into a canonical schema:

A_intro
A_methods
A_results
Each section is exported as a top-level field in the structured
JSON artifact rather than as a nested dictionary. This design
simplifies downstream validation and embedding workflows.

Missing sections are represented using the sentinel value:

SECTION_NOT_FOUND