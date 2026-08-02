# Holodori Optimizer

A browser-based team optimizer for **hololive Dreams**. Import your roster from screenshots, optimize a five-card team, build around an oshi, compare teams, and estimate which unowned 5★ card would improve your roster the most.

> **Unofficial fan project.** This project is not affiliated with or endorsed by COVER Corp., hololive production, QualiArts, Inc., or HolodoriDB. See [LEGAL_NOTICE.md](LEGAL_NOTICE.md).

## Current release

**v3.8.15**

The easiest way to use the optimizer is to download the release package, keep the HTML and chart-data file together, and open the HTML in a modern desktop browser.

If you are using this repository directly:

1. Open `dist/Holodori_Optimizer_v3.8.15.html`.
2. Keep `dist/Holodori_Chart_Data_r51.js` in the same folder if you want **Choose a song** scoring.
3. Import roster screenshots or edit your roster manually.

No server, npm install, account, or build step is required for normal use.

## What it does

- **Best Team** — finds the strongest team from your owned roster.
- **Build around my oshi** — requires an exact selected oshi card while optimizing the rest of the team.
- **Best next card** — tests unowned **5★** acquisition candidates and estimates which one improves your roster most, either for any team or for a team containing your selected oshi.
- **Compare teams** — compares two manually configured teams using the same scoring terminology and model.
- **Roster screenshot import** — recognizes current 3★–5★ cards, Level, and Bloom from supported desktop/mobile roster screenshots, with a review step before applying changes.
- **Any song / Choose a song** — uses either the calibrated average-chart model or a bundled validated Perfect-FC chart timeline.
- **Holomem Board** — can optimize the currently modeled **Frequency Up** nodes in 0–3-node allocations per eligible Member, using a shared 0–12-node budget. Other Board effects are intentionally not modeled yet.

## Important model limitations

The score shown by the optimizer is a **comparative expected index**, not the game's literal displayed score. The current model assumes Perfect Full Combo and may omit or approximate mechanics that are undocumented or not yet represented.

Currently omitted or incomplete systems include:

- Holomem Board effects other than Member **Frequency Up** nodes
- Leader Board bonuses
- Memory bonuses
- Member Power-Up bonuses
- Fever / multiplayer effects
- hidden rounding or undocumented game logic

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and the validation records for implementation details.

## Roster recognition

Roster recognition runs locally in the browser in a Web Worker. The current embedded registry covers **167 cards** across 3★, 4★, and 5★ rarities. Overlapping screenshots are deduplicated, and unresolved rows are held for review rather than silently applied.

The recognizer is validated on the desktop and mobile layouts included in the project's regression set, but no computer-vision importer can guarantee every future UI layout, severe crop, compression level, or newly released card without an updated reference registry.

## Artwork and network use

The optimizer does **not** bundle card artwork. Card portraits and small presentation assets may be requested from HolodoriDB when artwork is enabled. Those images are presentation-only and do not affect scoring.

Owned-card/progression settings are stored locally in browser storage. There is no built-in account system or analytics.

See [LEGAL_NOTICE.md](LEGAL_NOTICE.md) for third-party content, attribution, privacy, and rights-holder information.


## GitHub Pages

The repository includes a root `index.html` that opens the current build in `dist/`. If GitHub Pages is enabled with the repository root as the publishing source, the optimizer will open from the repository's Pages URL.

## Development

The project deliberately avoids a JavaScript build ecosystem. The release HTML is generated with Python's standard library:

```bash
python build.py dist/Holodori_Optimizer_v3.8.15.html
```

The build is deterministic. The expected SHA-256 for the current HTML is recorded in `RELEASE_TARGET_SHA256.txt`.

Main source boundaries:

- `src/template.html` — document structure
- `src/styles.css` — presentation
- `src/app.js.in` — browser UI/orchestration
- `src/search_worker.js` — scoring and search engine
- `src/roster_importer.js.in` — screenshot-import adapter
- `src/roster_recognizer/` — recognition worker and reference data
- `validation/` — regression/QC records
- `versions.json` — app/model/data version boundaries

More detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Data and attribution

Structured card/master data is derived from **HolodoriDB / holodori.best**. The project does not claim ownership of hololive Dreams artwork, characters, trademarks, game data, or other third-party material.

## License

No open-source license has been granted for the original optimizer source at this time. See [LICENSE](LICENSE). Third-party game/art/data rights are separate and are not granted by this repository.
