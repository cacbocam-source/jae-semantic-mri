# Bridge Robustness Audit

This folder contains bridge-boundary audit evidence supporting the route-aware semantic corpus pipeline manuscript.

## Purpose

The audit evaluates whether flagged section-recovery conditions in the 1995–1999 legacy boundary epoch and 2000–2004 modern boundary epoch affected the bridge transition metric.

## Files

- `bridge_boundary_summary_1995_2004.md`: Human-readable bridge-boundary audit summary.
- `bridge_boundary_summary_1995_2004.json`: Machine-readable bridge-boundary audit summary.
- `bridge_boundary_doc_audit_1995_2004.csv`: Document-level bridge-boundary audit records.
- `bridge_transition_innovation_velocity.csv`: Bridge-transition and adjacent-epoch metric output.
- `epoch_centroids_reduced.csv`: Reduced centroid coordinates used for model-validation visualization.

## Audit Interpretation

The baseline bridge value was calculated from all contributing manuscripts in the 1995–1999 and 2000–2004 boundary epochs.

The sensitivity audit showed that excluding flagged boundary-epoch manuscripts changed the bridge estimate. The legacy-only exclusion condition produced an absolute bridge delta of 0.005302, and the complete-case condition produced an absolute bridge delta of 0.004824.

These results should not be interpreted as evidence that the bridge estimate is invariant under aggressive filtering. Instead, they support a conservative interpretation: boundary filtering can affect the bridge estimate, and the bridge transition should be retained as a descriptive continuity indicator rather than treated as a stand-alone inferential finding.

## Short-Section and Flagging Caution

The audit flagging logic includes explicit missing-section indicators and short-section conditions. Short-section screening may conflate extraction fragility with legitimate variation in article brevity, section density, historical genre conventions, or concise but valid reporting.

For that reason, the stricter flagged-case exclusions are preserved as conservative sensitivity stress tests rather than adopted as the primary completeness criterion for the manuscript analysis.

## Manuscript Boundary

These files support methods-validation transparency only. They are not used to make substantive claims about intellectual change in the JAE archive.
