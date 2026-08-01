Holodori Team Optimizer v2.2.0
==============================

WHAT v2.2 CHANGES
-----------------
v2.2 is the first hybrid Python + browser release.

The user-facing optimizer remains a standalone HTML/JavaScript application. Python is NOT required to open or use it.

Python is now the canonical development/build layer for:
- reading the HolodoriDB repository ZIP/directory (or fetching the public raw tables),
- normalizing relational game data into the optimizer card model,
- validating schema/content,
- packing repeated level/Bloom data for the standalone HTML,
- producing release manifests/hashes,
- retaining card asset IDs for future images,
- materializing card progression for tests,
- independently evaluating ordered teams as a reference scorer,
- cross-language regression tests against the production JavaScript worker.

The scalable v2.1 beam-search engine is intentionally preserved in the browser runtime while the surrounding project architecture is made maintainable.

TOP-LEVEL FILES
---------------
- Holodori_Optimizer_v2.2.0.html
  Standalone optimizer. Open directly in a modern browser.

- HolodoriDB_Bundled_Normalized_Snapshot.json
  Human-readable schema-v2 card/master snapshot used to build the release.

- HolodoriDB_Card_Asset_Manifest.json
  Compact card ID -> Holodori assetId mapping plus basic display metadata. This is a forward hook for card artwork/image resolution.

- BUILD_MANIFEST.json
  Source DB version, card counts, asset-ID coverage, build metadata, and SHA-256 hashes for core release/build artifacts.

- QC_REPORT.txt
  Release-specific quality-control results.

- developer/
  Reproducible Python build/update/reference-QC toolchain and the browser source template/worker.

DATA SOURCE & CREDITS
---------------------
Card/master data come from the HolodoriDB / holodori.best database, provided and maintained by prodeode (Discord) and used with permission.
The canonical release pipeline normalizes the public HolodoriDB/holodori-db-eng-diff JSON.

Bundled source version:
0b8b02c061dd6900cac86860443e3dfea22b8efe5ccc424b3b99a67821acc3be

Bundled counts:
- 59 five-star cards
- 54 four-star cards
- 54 three-star cards
- 167 total cards
- 167/167 cards retain an assetId

SCHEMA v2
---------
The scoring fields intentionally remain compatible with v2.1. Schema v2 adds card.assetId so future image support can be implemented without another card-data migration.

The Python normalizer was regression-tested against the v2.1 normalized snapshot: after removing the intentional schemaVersion/assetId additions, the current 167-card data are semantically identical.

RUNTIME / UPDATE BEHAVIOR
-------------------------
The HTML starts immediately from its Python-built, validated bundled snapshot.

For convenience, the existing browser-side HolodoriDB update checker is retained. That compatibility normalizer is separately regression-tested against the Python normalizer. A failed network/schema update never replaces the last-known-good data.

The released HTML does not require Python, Node, a server, or an installation.

SEARCH ARCHITECTURE
-------------------
v2.2 preserves the scalable v2.1 search strategy:
1. static card-potential ordering,
2. incremental partial-team expansion,
3. global beam plus attribute/group synergy-rescue lanes,
4. bounded later-depth extension sets,
5. quick full-team screening,
6. local one-card-swap polishing,
7. representative-order full-model refinement,
8. exhaustive 5! = 120 order verification for the strongest finalists.

Fast / Balanced / Thorough control the size of the candidate frontier and final verification set.

This remains a heuristic best-found optimizer, not a mathematical proof that every pruned composition cannot be globally optimal. Retained finalists use the documented full scoring model.

SCORING MODEL
-------------
The runtime includes the same principal v2.1/v2.0.2 scoring model:
- Level/Bloom-dependent card progression
- Performance / Technique / Sense
- structured Passive targets and conditions
- Active probability, interval, duration, conditional magnitude and overlap
- Score Support
- Special direct contribution and Special-position weighting
- Skill Activation Rate (SAR) approximation
- Outfit Skills, including conditional and external Outfit use
- team-order optimization

The objective remains an Expected Stat x Score index, not a literal prediction of the game's displayed Unit Score.

CURRENT EXCLUSIONS / ASSUMPTIONS
--------------------------------
- Holomem Board bonuses excluded
- Memory bonuses excluded
- Member Power-Up bonuses excluded
- Skill Tree Connect/Board score effects excluded
- exact chart note density/timestamps unavailable
- exact SAR-to-Active-check alignment unavailable
- gameplay-state conditions such as Combo/LIFE/judgement thresholds are assumed satisfied where documented
- non-scoring lower-rarity secondary effects may be retained as unsupported metadata but do not add score

DEVELOPER QUICK START
---------------------
The included Python toolchain uses only the Python standard library.

Rebuild from a downloaded HolodoriDB ZIP or checkout:

  python developer/python/build_release.py --db /path/to/holodori-db-eng-diff-main.zip --out rebuilt

Fetch the public raw tables and rebuild:

  python developer/python/build_release.py --fetch --out rebuilt

Run normal QC against the packaged release:

  python developer/tests/run_qc.py

Run raw-normalizer + exact-subset regression checks too:

  python developer/tests/run_qc.py --raw /path/to/holodori-db-eng-diff-main.zip --search-regression

Run the expensive 893-million-space stress test as well:

  python developer/tests/run_qc.py --raw /path/to/holodori-db-eng-diff-main.zip --search-regression --large-search

Node.js is optional for building, but is used by the cross-language JavaScript QC tests when available.

See developer/DEVELOPER_GUIDE.txt for architecture details.

CHANGELOG
---------
v2.2.0 — 1 August 2026
- Introduced hybrid Python + standalone-browser architecture.
- Added zero-dependency Python raw-data normalization/validation/packing/release build pipeline.
- Added Python reference card materializer and ordered-team scoring model.
- Added Python <-> browser normalization/materialization/scoring regression tests.
- Added BUILD_MANIFEST.json with hashes/build metadata.
- Added HolodoriDB_Card_Asset_Manifest.json.
- Added assetId to schema v2 / materialized cards for future image support.
- Preserved the v2.1 search/scoring behavior.
