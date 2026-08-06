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
- Songs: **177**
- Exact chart pack: **r51**
- Chart metadata rows: **708**
- Exact timelines: **702**
- Packed note events: **405,194**

## Integrity

Standalone HTML SHA-256: `af579c6c8a719ee8a3a74539161e89cd596b4ec64f7801b550c5ed668c2162e2`
