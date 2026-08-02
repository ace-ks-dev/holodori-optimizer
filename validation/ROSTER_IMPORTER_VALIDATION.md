# Roster Screenshot Importer v1.0.1 — validation

The v3.7.0 release retains the browser-native recognizer validated in v3.6.x. It uses generated 3★–5★ card references, roster-grid geometry, metadata filtering, visual matching, Level/Bloom glyph recognition, and cross-screenshot perceptual deduplication.

## Current reference scope

- 167 current cards indexed: 54 × 3★, 54 × 4★, 59 × 5★.
- Recognition logic contains no card/member-specific branches.
- New cards are added by refreshing registry/reference data, not by adding per-card code.
- Runtime compares the embedded recognition registry with the optimizer registry and fails closed if they diverge.

## Recognition regressions

- Original overlapping roster: 49 physical detections → 31 unique cards; 31/31 identity; 31/31 Level and Bloom after deduplication.
- Mixed-rarity fixture: 18/18 identities; all visible progression resolved, clipped progression left for review/overlap.
- Independent validation pair: 36/36 identities.
- Identity across 65%, 80%, 100%, 120%, and 130% image scale: 25/25 screenshot cases exact.
- Progression scale extremes: 8/8 cases exact for visible Levels/Blooms.
- JPEG Q55/Q75/Q90: 12/15 cases fully automatic exact; the remaining cases conservatively produced review rows rather than forced wrong identities.

## v3.7 integrated smoke

- A current validation screenshot produced 18 review rows in ~0.5 s in the built browser app.
- Max-Level normalization is checked by default.
- Applying the review updated the quick roster summary to 18 cards / 18 Holomems.
- No page errors were observed.

## Boundary

Recognition still writes only through the owned-progression adapter and does not implement or alter score equations. `scoringModelVersion` remains `PFC-v3.5.0`. v3.7 changes the search worker only for oshi-constrained candidate selection / oshi-Outfit selection; the recognition worker and index are unchanged from v3.6.1.
