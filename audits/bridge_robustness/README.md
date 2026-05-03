# Bridge Robustness Audit

This folder contains bridge-boundary audit evidence supporting the route-aware semantic corpus pipeline manuscript.

## Purpose

The audit evaluates whether explicit missing-section placeholder indicators in the 1995–1999 legacy boundary epoch materially affected the legacy centroid used in the bridge transition metric.

## Primary Manuscript Evidence

The primary robustness condition is the placeholder-only audit. This condition excludes manuscripts with explicit missing-section placeholder indicators from the 1995–1999 legacy boundary epoch and evaluates the resulting legacy-centroid shift.

The manuscript uses this audit as methods-validation evidence only. It does not support substantive interpretation of intellectual change in the JAE archive.

## Supporting Files

- `bridge_boundary_summary_1995_2004.md`: Human-readable bridge-boundary audit summary.
- `bridge_boundary_summary_1995_2004.json`: Machine-readable bridge-boundary audit summary.
- `bridge_boundary_doc_audit_1995_2004.csv`: Document-level bridge-boundary audit records.
- `bridge_transition_innovation_velocity.csv`: Bridge-transition and adjacent-epoch metric output.
- `epoch_centroids_reduced.csv`: Reduced centroid coordinates used for model-validation visualization.

## Interpretation Boundary

The bridge robustness audit supports the interpretation that residual extraction artifacts at the 1995–1999 boundary did not materially bias the bridge estimate under the primary placeholder-only condition.

Short-section or aggressive completeness screens, if retained in the audit record, should be interpreted as conservative sensitivity stress tests rather than primary completeness criteria because they may conflate extraction fragility with legitimate variation in article brevity, section density, or historical genre conventions.
