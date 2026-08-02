# Browser roster recognizer data

This directory is deliberately isolated from optimizer scoring/search.

- `worker.js` — browser recognition pipeline.
- `cards.json` — normalized 3★–5★ recognition registry.
- `references.json` — compact generated visual index (dense-rgb-v1).
- `digit_templates.json` — Level/Bloom glyph templates.

`src/roster_importer.js.in` is the adapter between this worker and the existing Owned Cards store. Severe screen-edge fragments are filtered before recognition; inferred/occluded slots that still resolve confidently are retained, while unresolved remnants are skipped rather than promoted to user review.

## Future card refresh

Recognition is data-driven. For a new card-data snapshot:

1. regenerate the normalized 3★–5★ card registry using the same stable card IDs as the optimizer;
2. use `tools/all_rarity_reference_refresher.html` to download the current portrait reference cache;
3. rebuild the compact visual reference index from those portraits;
4. replace `cards.json` / `references.json` and rebuild the optimizer;
5. rerun the native, scale, and compression regression set.

Do not add card/member-specific branches to `worker.js`. Runtime import fails closed if the optimizer registry and recognition registry no longer match.
