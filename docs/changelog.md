# Changelog

## 0.1.0

Initial alpha release of the deterministic `feature-align/1` IPA metric.

- Added PanPhon-backed articulatory feature comparison.
- Added the bundled Standard German `de-DE` profile.
- Added sparse sequence equivalences for German syllabic-sonorant reductions and affricate notation.
- Added strict unsupported-segment validation and complete metric/profile/backend provenance.
- Defined the v0.1 metric as stress-insensitive.
- Added score-only operation-free mode and optional explainable alignment.

This release is alpha quality. Numeric profile costs are engineering parameters
that require calibration against reviewed benchmark examples. The metric is not
a validated human perceptual or acoustic similarity model.
