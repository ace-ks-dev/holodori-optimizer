# Holodori Optimizer v3.14.0-beta.23

## Difficulty-calibrated Any song

- **Any song now asks for Easy / Normal / Hard / Expert.** The selected difficulty uses its own six weighted scenarios instead of pooling all four difficulty populations together.
- The current r53 calibration is derived from **722 exact Perfect-FC timelines**: 180 Easy, 180 Normal, 181 Hard, and 181 Expert.
- Optimizer results retain their Any-song difficulty, and loading a result into Compare carries that calibration context with the team.
- The chosen Any-song difficulty is remembered locally after selection.

## Maintenance hardening

- Added a deterministic Any-song scenario generator derived from the active protected chart pack and canonical chart metadata.
- Chart promotion now regenerates the calibration automatically.
- Gated public builds regenerate against the exact chart population that is actually published, preventing embargoed/current-only charts from leaking into generic scoring.
- Static maintenance gates reject stale scenario revisions, timeline counts, difficulty sets, or malformed 6-scenario / 2-screening payloads.

## Protected mechanics

The protected scorer/search worker, roster importer, roster recognizer worker, Holomem Board mechanics, and canonical card mechanics are unchanged from beta.22. Any-song team scores and rankings can legitimately differ because the existing scorer now receives difficulty-appropriate chart-duration, note-count, combo, and coefficient scenarios.

## Included data

- Cards: **169**
- Songs: **182**
- Exact chart pack: **r53**
- Chart metadata rows: **728**
- Exact timelines: **722**
- Packed note events: **416,423**

## Integrity

Standalone HTML SHA-256: `6083b50dcb9772e3b70cf2460da73d2ac0288ba711b15de77509bd2f448dca8e`
