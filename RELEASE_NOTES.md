# Holodori Optimizer v3.14.0-beta.15 — Any-song Details Hotfix

This release fixes Team-details diagnostics in the current Any-song scoring architecture.

## Fixed

- Restored numeric **Proc** and **Active** values in **Skill summary by position**.
- Removed the invalid `slot ×NaN` Special-support diagnostic.
- Any-song Special rows now show scenario-weighted average trigger times.
- Any-song SAR windows now come from the same scenario profile used for scoring.
- Corrected exact-chart Special/SAR detail plumbing.

## Scoring behavior

This is a diagnostics/UI payload fix. Projected scores and optimizer rankings are unchanged from v3.14.0-beta.14 for the same included data.

## Included data

- Cards: **169**
- Songs: **182**
- Exact chart pack: **r53**
- Chart metadata rows: **728**
- Exact timelines: **722**
- Packed note events: **416,423**

## Integrity

Standalone HTML SHA-256: `f3e61608a9aa2abf19c22e2b49d0aef6dc486c3ae150ef1031f57e512edf8120`
