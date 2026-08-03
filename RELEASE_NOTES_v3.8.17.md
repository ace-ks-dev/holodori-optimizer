# v3.8.17 — urgent Passive targeting hotfix

This release fixes a core Passive-skill targeting bug in v3.8.16.

- `targetCount` is now treated only as the maximum number of eligible recipients, not as an activation prerequisite.
- Passive composition prerequisites now come only from the explicit game-data trigger (`LivePassiveSkillLevel.liveSkillTriggerGroupId`).
- This also fixes passives that require 2 matching members but can target up to 3; v3.8.16 incorrectly required 3.
- If more members qualify than the target limit, recipients are prioritized by highest current unbuffed Performance + Technique + Sense total, with left-to-right team position as the tie-breaker.
- The bundled card snapshot and runtime HolodoriDB refresh path are both corrected.
- No unreleased Holomem Board expansion or other post-v3.8.16 development work is included.

Validation: all 334 bundled Passive level rows were audited against corrected canonical mechanics derived from the exact same HolodoriDB source revision; targeted worker regressions and deterministic double-build checks passed.
