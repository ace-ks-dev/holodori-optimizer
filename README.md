# Holodori Team Optimizer

**Current stable release: v2.2.0**

A browser-based team optimizer for **Holodori**, built from structured [HolodoriDB](https://holodori.best/) game data.

The optimizer evaluates five-card teams using card progression, Passives, Active Skills, Specials, Skill Activation Rate effects, Outfit Skills, team order, and card-to-card conditions. It supports both personal-roster optimization and large global searches across the available card pool.

The public app remains a standalone HTML/JavaScript application. **Python is not required to use the optimizer.** Starting with v2.2.0, Python is used as the canonical development, data-build, validation, and reference-testing layer.

---

## Features

- Optimize a five-card team from your **owned roster**.
- Search the current **5★ pool** or **all 3★–5★ cards**.
- Respect the one-card-per-Holomem team restriction.
- Configure each owned card's **Level** and **Bloom** progression.
- Model **Performance / Technique / Sense** stat distributions.
- Model structured **Passive Skill** targets and conditions.
- Model **Active Skill** probability, interval, duration, conditional magnitude, and overlap.
- Model **Score Support** effects.
- Model direct **Special Skill** contribution and Special-position weighting.
- Approximate **Skill Activation Rate (SAR)** interactions with Active Skills.
- Optimize **Outfit Skills**, including conditional and external Outfit use.
- Optimize **team order**.
- Anchor searches around a chosen card/Holomem.
- Compare two teams directly.
- Choose **Fast**, **Balanced**, or **Thorough** global-search effort.
- Run very large searches without exhaustively enumerating every five-card combination.
- Save roster settings locally in the browser.

---

## Using the optimizer

### GitHub Pages

If this repository is published with GitHub Pages, open the Pages site and use the optimizer directly in your browser.

### Local use

Download `index.html` (or the standalone release HTML) and open it in a modern browser.

No installation, Python environment, Node.js, or local web server is required for normal use.

Your owned-card settings are stored in browser `localStorage`.

---

## Search modes

### Fast

Designed for normal use. Uses a relatively narrow candidate frontier and returns strong results quickly.

### Balanced

Searches a larger and more diverse candidate set before exact finalist evaluation.

### Thorough

Uses the broadest candidate frontier and largest finalist set. It is slower, but gives the heuristic search more opportunities to recover unusual synergy-heavy teams.

### Important: "best found" vs. proven optimum

The current global optimizer is a **heuristic best-found search**, not a formal mathematical proof of the global optimum.

The raw all-rarity search space already contains roughly **893 million valid five-card teams** in the current database. Exhaustively evaluating every team, every order, and every Outfit interaction would scale very poorly as more cards are released.

v2.2 therefore preserves the scalable v2.1 search architecture:

1. static card-potential ordering,
2. incremental partial-team expansion,
3. global beam plus attribute/group synergy-rescue lanes,
4. bounded later-depth extension sets,
5. quick complete-team screening,
6. local one-card-swap polishing,
7. representative-order full-model refinement,
8. exhaustive `5! = 120` order verification for the strongest finalists.

Retained finalists are evaluated with the full implemented scoring model. The heuristic part is deciding which compositions survive to that stage.

---

## Scoring model

The optimizer currently models:

- Level/Bloom-dependent card progression
- Performance
- Technique
- Sense
- Passive stat buffs
- Passive Score Support
- attribute/group/generation targeting
- Top-N Passive recipients
- Active Skill activation probabilities
- Active interval and duration
- conditional Active Score UP
- overlapping Active Skills
- direct Special Skill contribution
- Special-position weighting
- Skill Activation Rate effects
- Outfit Skills
- conditional Outfit triggers
- external Outfit owners
- team-order effects

The primary optimization objective is an **Expected Stat × Score index**. It should not be interpreted as an exact prediction of the Unit Score displayed by the game.

---

## Current assumptions and exclusions

The following are not yet incorporated into the main optimizer model:

- Holomem Board bonuses
- Memory bonuses
- Member Power-Up bonuses
- Skill Tree Connect/Board scoring effects
- exact chart note density and note timestamps
- exact in-game Special timestamps
- exact SAR-to-Active-check alignment
- undocumented or hidden scoring mechanics

Gameplay-state conditions such as Combo, LIFE, or judgement thresholds are currently assumed to be satisfied where required by the documented skill.

Some lower-rarity secondary effects may be retained as unsupported metadata without contributing score until their scoring behavior is implemented.

---

## Data source

Card and master data are derived from **HolodoriDB / holodori.best**, maintained by **prodeode**, and used with permission.

The v2.2.0 bundled snapshot was built from HolodoriDB source version:

```text
0b8b02c061dd6900cac86860443e3dfea22b8efe5ccc424b3b99a67821acc3be
```

Bundled card counts:

| Rarity | Cards |
|---|---:|
| 5★ | 59 |
| 4★ | 54 |
| 3★ | 54 |
| **Total** | **167** |

All 167 current cards retain their Holodori `assetId` in schema v2 for future artwork/image integration.

---

## v2.2 architecture

v2.2 is the first hybrid Python + browser release.

```text
HolodoriDB raw data
        │
        ▼
Python build / normalization / validation
        │
        ├── normalized card snapshot
        ├── asset manifest
        ├── build manifest
        └── reference scoring / QC
        │
        ▼
Standalone HTML + JavaScript application
        │
        ▼
Web Worker search + scoring engine
```

### Browser layer

The browser application handles:

- user interface,
- roster management,
- local storage,
- team comparison,
- production scoring,
- scalable team search.

### Python layer

The Python tooling handles:

- reading a HolodoriDB repository ZIP or directory,
- joining relational master-data tables,
- normalization into the optimizer card model,
- schema/content validation,
- card progression materialization,
- snapshot packing,
- release manifests and SHA-256 hashes,
- card `assetId` preservation,
- independent reference scoring,
- Python ↔ JavaScript regression testing.

The Python toolchain uses only the Python standard library.

---

## Repository layout

A typical v2.2 repository looks like:

```text
.
├── index.html
├── HolodoriDB_Bundled_Normalized_Snapshot.json
├── HolodoriDB_Card_Asset_Manifest.json
├── BUILD_MANIFEST.json
├── README.md
├── QC_REPORT.txt
└── developer/
    ├── DEVELOPER_GUIDE.txt
    ├── python/
    │   ├── build_release.py
    │   ├── update_snapshot.py
    │   └── holodori_optimizer/
    ├── source/
    │   ├── optimizer_template.html
    │   └── worker.js
    └── tests/
```

---

## Developer quick start

### Rebuild from a downloaded HolodoriDB ZIP or checkout

```bash
python developer/python/build_release.py \
  --db /path/to/holodori-db-eng-diff-main.zip \
  --out rebuilt
```

### Fetch the public raw tables and rebuild

```bash
python developer/python/build_release.py --fetch --out rebuilt
```

### Run normal QC

```bash
python developer/tests/run_qc.py
```

### Include raw-normalizer and exact-subset regression checks

```bash
python developer/tests/run_qc.py \
  --raw /path/to/holodori-db-eng-diff-main.zip \
  --search-regression
```

### Include the large all-rarity search stress test

```bash
python developer/tests/run_qc.py \
  --raw /path/to/holodori-db-eng-diff-main.zip \
  --search-regression \
  --large-search
```

Node.js is optional for building the release, but is used for cross-language JavaScript QC when available.

See `developer/DEVELOPER_GUIDE.txt` for additional architecture details.

---

## Quality control

v2.2 introduced an independent Python reference implementation specifically to reduce the risk of silently changing the scoring model while the browser optimizer evolves.

Release QC includes:

- raw HolodoriDB normalization checks,
- Python ↔ JavaScript normalized-data comparison,
- randomized Level/Bloom materialization comparison,
- randomized ordered-team scoring comparison,
- exact small-pool search regression against the earlier exhaustive optimizer,
- full 5★ regression,
- all-rarity scalability testing,
- external/fixed Outfit tests,
- owned-roster tests,
- anchored-card tests,
- Team Comparison tests,
- final JavaScript syntax checks,
- release/package integrity checks,
- reproducible-build verification.

The v2.2 release artifacts can be rebuilt from the packaged developer tooling and HolodoriDB source data.

---

## Card images

v2.2 lays the groundwork for future card artwork support without coupling images to the scoring engine.

Each normalized card retains its source `assetId`, and the release includes:

```text
HolodoriDB_Card_Asset_Manifest.json
```

The intended architecture is for artwork to remain a presentation-layer feature. Failure to load an image should never affect optimization or scoring.

---

## Changelog

### v2.2.0 — 1 August 2026

- Introduced the hybrid Python + standalone-browser architecture.
- Added a zero-dependency Python normalization, validation, packing, and release-build pipeline.
- Added a Python reference materializer and ordered-team scorer.
- Added Python ↔ JavaScript normalization/materialization/scoring regression tests.
- Added `BUILD_MANIFEST.json` with release hashes and build metadata.
- Added `HolodoriDB_Card_Asset_Manifest.json`.
- Added `assetId` to schema v2 for future image support.
- Preserved the scalable v2.1 search and scoring behavior.

### v2.1.x — development milestone

- Replaced exhaustive complete-team enumeration with scalable bounded search.
- Added all-rarity optimization.
- Added Fast / Balanced / Thorough effort modes.
- Added local team polishing and improved finalist/order evaluation.
- Added search-space instrumentation.

### v2.0.x — development milestone

- Rebuilt card mechanics around normalized HolodoriDB master data.
- Added structured Passives, Active Skills, Specials, SAR, and Outfit Skills.
- Added external Outfit optimization.
- Added Level/Bloom progression support.

### v1.5.2

Previous public stable release.

---

## Disclaimer

This is a fan-made optimization tool. Game mechanics may change, database interpretations may be incomplete, and undocumented in-game behavior may differ from the implemented model.

Results should therefore be treated as analytical recommendations under the documented optimizer assumptions rather than authoritative in-game guarantees.
